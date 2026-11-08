# MiniMaxH3 长视频操作台（lanxi）

独立 ComfyUI 插件，只注册两个节点：

- **MiniMaxH3长视频操作台（lanxi)** — 1‑8 段分段编排、每段首/尾帧、参考图/视频/音频、RefMod、LoRA
- **MiniMax-H3 长视频分段采样（lanxi）** — 分段采样、潜空间续接、音视频解码与拼接

节点 ID、socket 类型和 API 路由都使用 lanxi 命名空间，避免与 GH/RefMod 旧插件冲突。

## 安装

1. 将仓库放到 ComfyUI/custom_nodes/ComfyUI-MiniMaxH3-lanxi；
2. 重启 ComfyUI；
3. 搜索 lanxi，添加上述两个节点。

## 说明

- 分段参考中的图片/视频/音频可拖动排序；
- 视频参考的喇叭开启时其原声作为音频参考，关闭则无音频参考；
- 单独上传的音频在没有视频原声时作为 <Audio 1>；
- 分段提示词框支持鼠标滚轮滚动。

