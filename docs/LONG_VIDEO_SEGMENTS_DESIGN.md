# 长视频多段续接（已实现）

> 一体化节点新增 **长视频分段** 模式 + 新节点 **MiniMax-H3 长视频分段采样(GH)**。
> 本文是实现说明与接线参考；使用步骤见仓库根目录 README。

## 1. 结构

- **一体化节点**：负责分段配置（1–8 段）、共享设置、每段素材/提示词/RefMod/LoRA，构建并输出 `segments` 计划（`MINIMAX_H3_SEGMENTS`）；同时为“运行范围首段”生成 `>` 预览 bundle。
- **长视频采样器**：按范围逐段执行：应用该段 LoRA → 构建 conditioning（上一段尾帧/末 N 帧作首帧）→ 双时钟采样 → 解码 → 裁掉重叠帧 → 拼接。
- 采样器内部加载 CLIP/VAE（由计划里的文件名），画布尺寸全局统一，保证帧可拼接。

## 2. 接口

### 一体化节点

| 方向 | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| 输入 | `main_mode` | 隐藏 COMBO | `text_keyframes` / `all_reference` / `multi_segment` |
| 输入 | `segments_json` | 隐藏 STRING | 分段表（面板维护） |
| 输出 | `>` | `MiniMax` | 单段模式原样；多段模式为范围首段预览 |
| 输出 | `mods` | `H3_REF_MODS` | 单段/首段 RefMod 列表 |
| 输出 | `segments` | `MINIMAX_H3_SEGMENTS` | 分段计划，接采样器 |

### 长视频采样器 `MiniMaxH3LongVideoRunnerGH`

输入：`model`、`segments`、`steps`(4)、`shift_video`(12)、`shift_audio`(3)、`sampler_name`、`scheduler`、`seed`(0)、`seed_policy`(increment/fixed)、`cfg`(1.0)、`release_clip`(true)、`free_between_segments`(true)。

输出：`frames`(IMAGE)、`audio`(AUDIO)、`last_frame`(IMAGE)、`report`(STRING)、`segment_info`(STRING JSON)。

## 3. 分段配置（`segments_json`）

```json
{
  "version": 1,
  "segments": [
    {
      "duration": 5,
      "prompt": "…<Picture 1>…<Video 1>…",
      "first_frame": "start.png",
      "images": ["a.png", "b.png"],
      "videos": [{"name": "v.mp4", "muted": false}],
      "audios": [{"name": "a.wav", "trimStart": 0, "trimEnd": null}],
      "mods": [{"name": "characterA", "strength": 1.0, "count": 1}],
      "loras": [{"name": "style.safetensors", "strength_model": 0.8}]
    }
  ],
  "range": {"start": 1, "end": 4},
  "overlap_frames": 20
}
```

限制：1–8 段；每段 6 图 / 2 视频 / 3 音频 / 8 RefMod / 4 LoRA；时长 2–30 秒；重叠 1–20 帧。

标签规则（每段独立）：首帧/续接帧 `<Picture 1>`；参考图接在首帧之后；RefMod 从 `<Video 1>` 开始；参考视频接在 RefMod 之后；音频按“未静音视频音轨 → 独立音频”排序。

## 4. 执行流程

```
for i in range(start, end):
    bundle = preview(i) 或 build_segment(i, first_frame = 上一段末 N 帧中的第一帧)
    model_i = base_model.clone(); 依次应用该段 4 个 LoRA（仅模型强度）
    采样：setup_dual_clock_sampling_gh + CFGGuider(cfg=1) + 双时钟 sampler
    解码：decode_av_latent → frames/audio
    i > start 时裁掉前 N 帧与对应音频
    记录 last_frame；释放缓存（可选）
拼接 frames/audio → 输出
```

要点：

- LoRA 只 patch 该段 MODEL，CLIP 不受影响（因此提示词编码始终用基础文本编码器）；
- 每段采样前可卸载文本编码器（`release_clip=true`），避免 CLIP 与 DiT 同时占显存；
- 画布在计划阶段按首段首个视觉素材（或 16:9）一次算好，所有段共用；
- 音频无交叉淡化，帧级续接可能有轻微跳变。

## 5. 接线

```
[Load Diffusion Model] ─────────────▶ MiniMax-H3 长视频分段采样(GH)
[一体化节点].segments ──────────────▶        │
                                             ├─ frames ─┐
                                             ├─ audio ──┴─▶ VHS_VideoCombine
                                             ├─ last_frame
                                             └─ report / segment_info
```

- 不要把分段 LoRA 提前串在 MODEL 上（会污染所有段）；
- 单段调试：切回首尾帧/全能参考模式，`>` 接适配器，工作流不变；
- 断点续跑：运行范围设为 A–B，给 A 段上传“上一段尾帧”作为首帧。

## 6. 已知限制

| 项 | 说明 |
| --- | --- |
| 帧级续接 | 末 N 帧只作为下一段首帧条件，不是 latent 连续；色彩/运动可能轻微跳变 |
| 范围与标签 | 范围内首段没有自动续接帧，其后各段 `<Picture 1>` 是续接帧；修改范围后需检查图片标签 |
| 音频 | 直接拼接，无交叉淡化，段间音色可能跳变 |
| 二采 | 循环内不做 tiled 二采；建议先出低清再后期处理 |
| 显存/耗时 | 每段独立采样；默认分段间卸载 CLIP 会明显增加耗时，显存足够可关闭 |
| LoRA | 仅模型强度；CLIP 侧 LoRA 不参与分段 |
