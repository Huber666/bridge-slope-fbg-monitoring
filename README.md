# 桥梁边坡光栅阵列监测方案

本项目研究桥台及道路邻近边坡病害的早期微变形感知：先明确病害及其可测前兆，再设计横向FBG光栅阵列、传力节点和室内病害模块，最后以独立参考和对照试验检验检测限及提前量。CNN-LSTM作为后续算法候选。文档按版本分目录保存。

**最新入口：[V4.0横向光栅与微变形研究设计版](versions/v4.0-transverse-microstrain/README.md)，2026-10-28。** 四册MD/DOCX、19项文献与资料、28项病害/过程/征兆清单、7张原创图和记录模板已整理；34页逐页核查完成。样件、土工参数、结构签审和检测性能仍须实物验证，具体见[发布核查记录](versions/v4.0-transverse-microstrain/发布核查记录.md)。V1—V3为历史基线，不与V4混用尺寸、点位、水量或性能目标。

## 版本目录

| 目录 | 内容 | 日期与状态 |
|---|---|---|
| [versions/v4.0-transverse-microstrain](versions/v4.0-transverse-microstrain/README.md) | 早期病害文献、横向FBG与转换节点、模块土箱制造、微变形实验与评价 | 2026-10-28；研究设计版，文件核查完成、实物待验证 |
| [versions/v1-initial](versions/v1-initial/README.md) | 早期文献选型、模型/现场施工初稿及FBG施工初稿 | 主体编写于2026-09-21，部分文件保留2026-10-12后续说明；作为历史讨论 |
| [versions/v2.2-manufacturing](versions/v2.2-manufacturing/README.md) | 模型制造、光栅封装与安装、文献、现场比较及需求核查 | 2026-10-12；保留作制造安装参考 |
| [versions/v2.3-failure-model](versions/v2.3-failure-model/README.md) | 材料选择、实心分层结构、滑移/塌落触发、评价指标和训练标签 | 2026-10-13；保留作为前版 |
| [versions/v2.4-indoor-compact](versions/v2.4-indoor-compact/README.md) | 室内小型尺寸、文献与比例校核、制造安装、失稳及数据放行 | 2026-10-14；历史小型坡槽方案 |
| [versions/v2.5-solidworks](versions/v2.5-solidworks/README.md) | SolidWorks原生零件/装配、STEP、支架构造与质量预算校核 | 2026-10-14；历史三维构造讨论模型，未作结构加工签审 |
| [versions/v2.6-manuals](versions/v2.6-manuals/README.md) | 分开的模型制造装配手册、监测试验操作手册、配图和记录模板 | 2026-10-15；历史制造与试验基线 |
| [versions/v3.0-integrated](versions/v3.0-integrated/README.md) | V2.2～V2.6整合版：文献综合、模型设计、制造装配、光栅布设、监测试验、CAD和闭环自检 | 2026-10-17；上一版整合入口，保留来源追踪 |
| [sources](sources/README.md) | 用户提供的原始技术方案 | 源文件标题含v3，其版本号属于原始工程文件，独立于本项目模型方案V2.2 |

当前仅有上述实际保存的文件，未发现独立的V2/V2.1历史快照；不根据最新文件反向编造旧版。后续修改请在新版本目录中保存，并通过Git提交记录追踪。

## V4阅读顺序与实施范围

| 阅读顺序 | 内容 | Word |
|---|---|---|
| [01 病害与文献证据](versions/v4.0-transverse-microstrain/01_病害与文献证据.md) | 病害前兆、19项来源的理论/试验/结论、理论与实体对应及证据缺口 | [DOCX](versions/v4.0-transverse-microstrain/01_病害与文献证据.docx) |
| [02 横向布纤与封装设计](versions/v4.0-transverse-microstrain/02_横向布纤与封装设计.md) | 三横线九节点、方向盲区、双面FBG转换件、夹具锚片、制造封装与引线 | [DOCX](versions/v4.0-transverse-microstrain/02_横向布纤与封装设计.docx) |
| [03 病害模型制造与装配](versions/v4.0-transverse-microstrain/03_病害模型制造与装配.md) | 台架/模块土箱/后期坡槽、材料尺寸、土料配比与铺法、室内及现场比较 | [DOCX](versions/v4.0-transverse-microstrain/03_病害模型制造与装配.docx) |
| [04 实验与评价方案](versions/v4.0-transverse-microstrain/04_实验与评价方案.md) | 标定与干湿传力、独立参考、加载与水量、检测限/提前量/误报、标准方法 | [DOCX](versions/v4.0-transverse-microstrain/04_实验与评价方案.docx) |

首轮做1个A直应变样件及三种厚度B弯曲样件，完成三方向、温度、噪声和反力标定后，再做单线土中耦合。B土箱候选净尺寸s600×y800×高300 mm、土厚160 mm；主测线沿y横向，埋深d80。无局部差动时横向纤维可能对整块顺坡同动不敏感，算法不能弥补这一几何盲区。

本版采用砂/高岭土干质量100/0、95/5、90/10作为试配候选，含水率2/4/6%用于分组；不是已证实的最佳配方。先测土工性质与土锚拔滑，再决定扩展阵列和坡槽。与电阻片、独立位移和视频在同一误报预算下比较，不预设FBG已经优越。

V3及更早SolidWorks文件仍保存在原目录，未新增V4加工CAD。旧500 mm宽坡槽无法直接容纳本版800 mm横向阵列；后期坡槽的几何、坡度和比例需另行设计并说明1g相似限制。

![V4横向阵列与测点坐标](versions/v4.0-transverse-microstrain/assets/F02_横向阵列.png)

本仓库收录项目文档与自产示意图，论文仅给出处和研究摘要，未上传论文全文。未明确授权开放许可，仓库中不额外添加开源许可证。
