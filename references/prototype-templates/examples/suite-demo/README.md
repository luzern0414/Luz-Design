# suite-demo：多系统文档示例（一个小程序，一个后台）

一份文档，三个页签：**前端架构**、**小程序**、**管理后台**。两个系统页签各放一个可交互原型，分别由 `../generic-mini/spec.json`（手机，小程序）和 `../generic-admin/spec.json`（电脑，后台）构建。架构页签是虚构的通用内容，页面和路径取自这两个示例规格；换成自己的项目时整页换成项目的功能说明，系统数量和页签名也由项目定。

| 文件 | 作用 |
|---|---|
| `suite.json` | 套件规格：标题、结论、前端架构页签的内容（分层图、各层职责、页面地图、路由与权限、状态放在哪里、响应式断点、组件库与主题）、两个系统 |

## 生成

```
py -X utf8 scripts/build_prototype_suite.py references/prototype-templates/examples/suite-demo/suite.json --out <文档.html>            文档旁边放两个原型文件，切到页签才加载
py -X utf8 scripts/build_prototype_suite.py references/prototype-templates/examples/suite-demo/suite.json --out <文档.html> --inline   单文件
py -X utf8 scripts/build_prototype_suite.py references/prototype-templates/examples/suite-demo/suite.json --check                      只校验
```

字段、页签规则和与 Luz-Project 的 02-前端界面设计的对接见 [`../../shell/README.md`](../../shell/README.md)；测试是 `scripts/test_prototype_suite.py`。

想只试一个系统或换成别的规格：把 `systems` 里对应一项的 `spec` 改成自己的规格路径，`surface` 与 `kind` 要匹配（小程序、手机网页是 `phone`，后台、网站是 `wide`），规格用哪个模板（mini 或 admin）也要与 `kind` 一致。
