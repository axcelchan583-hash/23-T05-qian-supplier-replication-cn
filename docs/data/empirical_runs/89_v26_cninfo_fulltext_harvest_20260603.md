# v26 CNINFO Fulltext GenAI Harvest

Date: 2026-06-03

## Purpose

This run harvests CNINFO top-search `标题+全文` metadata for GenAI terms from `2023-01-01` to `2026-06-03`. It is the source-rebuild step for a Qian-scale China replication and for later China-specific GenAI disclosure research.

It does not download all PDFs. Search-result metadata and snippets are enough to build a recall pool, while full PDFs should be downloaded only after candidate ranking.

## Query Scope

- Endpoint: `https://www.cninfo.com.cn/new/fulltextSearch/full`
- Search mode: `标题+全文`
- Date range: `2023-01-01` to `2026-06-03`
- Page size: `100`
- Page cap per date shard: `200`
- Term mode: `all`
- Broad single term `人工智能` is excluded by design.

## Query Counts

| query_term | query_tier | query_start_date | query_end_date | query_shard_index | query_shard_count | query_shard_depth | total_records | target_pages | successful_pages | failed_pages | failed_page_numbers | failed_page_errors | page_size |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 大语言模型 | core_recall | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 10832 | 109 | 109 | 0 |  |  | 100 |
| 语言大模型 | core_recall | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 10834 | 109 | 109 | 0 |  |  | 100 |
| 生成式AI | core_recall | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 4924 | 50 | 50 | 0 |  |  | 100 |
| AIGC | core_recall | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 4744 | 48 | 48 | 0 |  |  | 100 |
| ChatGPT | core_recall | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 2302 | 24 | 24 | 0 |  |  | 100 |
| GPT | core_recall | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 1205 | 13 | 13 | 0 |  |  | 100 |
| DeepSeek | core_recall | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 2832 | 29 | 29 | 0 |  |  | 100 |
| 通义千问 | named_model | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 389 | 4 | 4 | 0 |  |  | 100 |
| 文心一言 | named_model | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 2 | 1 | 1 | 0 |  |  | 100 |
| 讯飞星火 | named_model | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 1459 | 15 | 15 | 0 |  |  | 100 |
| 星火认知 | named_model | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 903 | 10 | 10 | 0 |  |  | 100 |
| 盘古大模型 | named_model | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 733 | 8 | 8 | 0 |  |  | 100 |
| 腾讯混元 | named_model | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 4591 | 46 | 46 | 0 |  |  | 100 |
| 豆包 | named_model | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 360 | 4 | 4 | 0 |  |  | 100 |
| Kimi | named_model | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 156 | 2 | 2 | 0 |  |  | 100 |
| 智谱 | named_model | 2023-01-01 | 2024-09-16 | 1 | 2 | 1 | 12275 | 123 | 123 | 0 |  |  | 100 |
| 智谱 | named_model | 2024-09-17 | 2026-06-03 | 2 | 2 | 1 | 12209 | 123 | 123 | 0 |  |  | 100 |
| 百川智能 | named_model | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 100 |
| 生成式人工智能 | zero_or_exact_check | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 100 |
| 生成式人工智能服务 | zero_or_exact_check | 2023-01-01 | 2026-06-03 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 100 |
| 大模型 | broad_genai_recall | 2023-01-01 | 2023-06-06 | 1 | 8 | 3 | 15870 | 159 | 159 | 0 |  |  | 100 |
| 大模型 | broad_genai_recall | 2023-06-07 | 2023-11-09 | 2 | 8 | 3 | 13422 | 135 | 135 | 0 |  |  | 100 |
| 大模型 | broad_genai_recall | 2023-11-10 | 2024-04-13 | 3 | 8 | 3 | 6617 | 67 | 67 | 0 |  |  | 100 |
| 大模型 | broad_genai_recall | 2024-04-14 | 2024-06-30 | 4 | 8 | 4 | 11267 | 113 | 113 | 0 |  |  | 100 |
| 大模型 | broad_genai_recall | 2024-07-01 | 2024-09-16 | 5 | 8 | 4 | 8819 | 89 | 89 | 0 |  |  | 100 |
| 大模型 | broad_genai_recall | 2024-09-17 | 2025-07-26 | 6 | 8 | 2 | 19326 | 194 | 194 | 0 |  |  | 100 |
| 大模型 | broad_genai_recall | 2025-07-27 | 2025-12-29 | 7 | 8 | 3 | 12270 | 123 | 123 | 0 |  |  | 100 |
| 大模型 | broad_genai_recall | 2025-12-30 | 2026-06-03 | 8 | 8 | 3 | 18876 | 189 | 189 | 0 |  |  | 100 |
| 混元大模型 | broad_genai_recall | 2023-01-01 | 2023-11-09 | 1 | 4 | 2 | 15664 | 157 | 157 | 0 |  |  | 100 |
| 混元大模型 | broad_genai_recall | 2023-11-10 | 2024-09-16 | 2 | 4 | 2 | 14096 | 141 | 141 | 0 |  |  | 100 |
| 混元大模型 | broad_genai_recall | 2024-09-17 | 2025-07-26 | 3 | 4 | 2 | 9173 | 92 | 92 | 0 |  |  | 100 |
| 混元大模型 | broad_genai_recall | 2025-07-27 | 2026-06-03 | 4 | 4 | 2 | 15894 | 159 | 159 | 0 |  |  | 100 |
| 模型备案 | registry_recall | 2023-01-01 | 2023-11-09 | 1 | 4 | 2 | 14616 | 147 | 147 | 0 |  |  | 100 |
| 模型备案 | registry_recall | 2023-11-10 | 2024-09-16 | 2 | 4 | 2 | 12453 | 125 | 125 | 0 |  |  | 100 |
| 模型备案 | registry_recall | 2024-09-17 | 2025-07-26 | 3 | 4 | 2 | 8486 | 85 | 85 | 0 |  |  | 100 |
| 模型备案 | registry_recall | 2025-07-27 | 2026-06-03 | 4 | 4 | 2 | 13060 | 131 | 131 | 0 |  |  | 100 |

## Sample Flow

| stage | rows | announcements | firms |
| --- | --- | --- | --- |
| raw_query_hits | 280662 | 111935 | 5359 |
| dedup_announcements | 111935 | 111935 | 5359 |
| a_share_formal_rows | 111685 | 111685 | 5327 |
| priority_manual_event_candidate | 1289 | 1289 | 640 |
| candidate_pool_for_manual_review | 13900 | 13900 | 2306 |
| first_candidate_per_firm | 2306 | 2306 | 2306 |
| priority_first_candidate_per_firm | 640 | 640 | 640 |
| priority_2023_2024_first_candidate_per_firm | 263 | 263 | 263 |
| priority_2023_2024_top3_candidates_per_firm | 406 | 406 | 263 |

## Candidate Tiers

| candidate_tier | rows | announcements | firms |
| --- | --- | --- | --- |
| exclude_no_strict_genai_after_snippet | 97083 | 97083 | 5325 |
| backfill_or_noisy_doc_with_action | 7522 | 7522 | 1815 |
| strict_genai_context_without_action | 5089 | 5089 | 1485 |
| priority_manual_event_candidate | 1289 | 1289 | 640 |
| review_denial_or_uncertain_genai | 702 | 702 | 383 |

## Year Counts

| announcement_year | candidate_tier | rows | firms |
| --- | --- | --- | --- |
| 2023 | backfill_or_noisy_doc_with_action | 774 | 357 |
| 2023 | exclude_no_strict_genai_after_snippet | 31437 | 5118 |
| 2023 | priority_manual_event_candidate | 186 | 102 |
| 2023 | review_denial_or_uncertain_genai | 129 | 81 |
| 2023 | strict_genai_context_without_action | 692 | 305 |
| 2024 | backfill_or_noisy_doc_with_action | 1430 | 616 |
| 2024 | exclude_no_strict_genai_after_snippet | 25749 | 5134 |
| 2024 | priority_manual_event_candidate | 310 | 202 |
| 2024 | review_denial_or_uncertain_genai | 166 | 125 |
| 2024 | strict_genai_context_without_action | 1147 | 521 |
| 2025 | backfill_or_noisy_doc_with_action | 3015 | 1243 |
| 2025 | exclude_no_strict_genai_after_snippet | 24564 | 5129 |
| 2025 | priority_manual_event_candidate | 537 | 382 |
| 2025 | review_denial_or_uncertain_genai | 246 | 159 |
| 2025 | strict_genai_context_without_action | 1872 | 881 |
| 2026 | backfill_or_noisy_doc_with_action | 2303 | 1215 |
| 2026 | exclude_no_strict_genai_after_snippet | 15333 | 5039 |
| 2026 | priority_manual_event_candidate | 256 | 214 |
| 2026 | review_denial_or_uncertain_genai | 161 | 116 |
| 2026 | strict_genai_context_without_action | 1378 | 860 |

## Title Noise Flags

| title_exclusion_reason | rows | firms |
| --- | --- | --- |
| periodic_report | 44603 | 5303 |
| advisor_opinion | 21648 | 4753 |
| financing_or_incentive_support | 6830 | 1615 |
| esg_or_internal_control_report | 5932 | 2337 |
| offering_or_listing_document | 4686 | 1348 |
| exchange_inquiry_or_reply | 4239 | 1006 |
| annual_or_interim_summary | 2094 | 1260 |
| governance_meeting_materials | 623 | 245 |
| trading_anomaly_or_value_plan | 478 | 304 |
| shareholder_meeting_only | 460 | 404 |
| performance_meeting_or_ir | 204 | 121 |
| risk_or_commitment_filler | 183 | 117 |
| fund_or_index | 71 | 58 |

## Priority Candidate Examples

| sec_code | sec_name | announcement_date | announcement_title | candidate_tier | query_terms | matched_genai_terms | qian_recall_score | announcement_content |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002229 | 鸿博股份 | 2023-02-08 | 鸿博股份：关于股价异动的公告 | priority_manual_event_candidate | AIGC | AIGC | 7 | 将智算中心打造成为具备标杆示范作用的 AI 产学研基地，也将与战略合作伙伴宣亚国际等就新华社元宇宙项目“山海中国”、以及 AIGC |
| 300364 | 中文在线 | 2023-02-15 | 中文在线：关于与北京澜舟科技有限公司签订战略合作协议的公告 | priority_manual_event_candidate | AIGC;ChatGPT;大模型;大语言模型;语言大模型 | GPT;ChatGPT | 7 | 近年来，澜舟科技在其享有自主知识产权的“孟子轻量化预训练模型”基础上，进一步融入了类ChatGPT的底层关键技术 |
| 688039 | 当虹科技 | 2023-02-27 | 当虹科技：杭州当虹科技股份有限公司2022年度业绩快报公告 | priority_manual_event_candidate | AIGC | AIGC | 7 | 新行业布局以及产品持续创新需要，公司在视频处理核心算法、产品国产化替代、AR/VR/XR技术、车载智能娱乐座舱以及AIGC |
| 300418 | 昆仑万维 | 2023-02-28 | 昆仑万维：2022年度业绩快报 | priority_manual_event_candidate | AIGC;大模型 | AIGC | 7 | 本报告期，公司发布了“昆仑天工”AIGC全系列算法与模型，并宣布开源，用实际行动推动开源社区建设。 |
| 002463 | 沪电股份 | 2023-03-23 | 沪电股份：2022年度总经理工作报告 | priority_manual_event_candidate | ChatGPT;大模型;混元大模型 | GPT;ChatGPT | 7 | 近期OpenAI的ChatGPT的显著成功似乎为商业人工智能应用发展开启了新时代的大门，AI或将在未来 |
| 600522 | 中天科技 | 2023-03-23 | 中天科技：江苏中天科技股份有限公司关于召开终止分拆所属子公司上市事项投资者说明会召开情况的公告 | priority_manual_event_candidate | ChatGPT;大模型 | GPT;ChatGPT | 7 | /在 Al 时代，ChatGPT 的发展，对公司光纤光缆市场需求有无影响，是否要用更先进的产品来把计算撑大 |
| 002362 | 汉王科技 | 2023-03-24 | 汉王科技：2022年度总裁工作报告 | priority_manual_event_candidate | AIGC | AIGC | 6 | 业 务 模 式 和 体 系拓展数字经济、数字政府、数字社会各项业务RPA（机器人流程自动化）技术平台AIGC |
| 300418 | 昆仑万维 | 2023-03-24 | 昆仑万维：关于股价异动的公告 | priority_manual_event_candidate | AIGC;ChatGPT;大模型 | GPT;ChatGPT | 7 | 公司和北京奇点智源科技有限公司（以下简称“奇点智源”）合作开发中国版类ChatGPT，中国版类ChatGPT |
| 301185 | 鸥玛软件 | 2023-03-28 | 鸥玛软件：关于签署战略合作协议的公告 | priority_manual_event_candidate | ChatGPT | GPT;ChatGPT | 7 | ）交易双方 甲方：山东国家应用数学中心 乙方：山东山大鸥玛软件股份有限公司 （二）合作内容 1、类 ChatGPT |
| 688327 | 云从科技 | 2023-03-30 | 云从科技：第二届董事会第五次会议决议公告 | priority_manual_event_candidate | 大模型;模型备案 | 大模型 | 7 | 扣除发行费用后拟用于以下项目： 单位：万元 序号 项目名称 总投资额 拟使用募集资金额 1 云从“行业精灵”大模型研发项目 |
| 688327 | 云从科技 | 2023-03-30 | 云从科技：2023年度向特定对象发行A股股票预案 | priority_manual_event_candidate | ChatGPT;GPT;大模型;大语言模型;模型备案;生成式AI | GPT | 6 | 一个预训练的语言表征模型，采用设计的自监督任务进行模型训练，训练好的模型通可应用于多个自然语言处理任务 GPT |
| 688327 | 云从科技 | 2023-03-30 | 云从科技：第二届监事会第二次会议决议公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 扣除发行费用后拟用于以下项目： 单位：万元 序号 项目名称 总投资额 拟使用募集资金额 1 云从“行业精灵”大模型研发项目 |
| 688327 | 云从科技 | 2023-03-30 | 云从科技：2023年第一次临时股东大会会议资料 | priority_manual_event_candidate | 大模型;模型备案 | 大模型 | 7 | 扣除发行费用后拟用于以下项目： 单位：万元 序号 项目名称 总投资额 拟使用 募集资金额 1 云从“行业精灵”大模型研发项目 |
| 002015 | 协鑫能科 | 2023-04-02 | 协鑫能科：关于参与杭州星临科技有限责任公司增资扩股暨对外投资的公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 公司已在安徽签约建设百亿规模的液冷超级智算中⼼，为国产大模型的研发训练、各行业领域的“AI+”产业智能化升级 |
| 300418 | 昆仑万维 | 2023-04-03 | 昆仑万维：关于股价异动的公告 | priority_manual_event_candidate | AIGC;ChatGPT;大模型 | GPT;ChatGPT | 7 | 公司和北京奇点智源科技有限公司（以下简称“奇点智源”）合作开发中国版类ChatGPT，中国版类ChatGPT |
| 300418 | 昆仑万维 | 2023-04-10 | 昆仑万维：关于发布大语言模型“天工”3.5的公告 | priority_manual_event_candidate | AIGC;ChatGPT;大模型;大语言模型;语言大模型 | GPT;大语言模型;ChatGPT | 7 | 年 2 月 9 日宣布将在今年内发布中国版类 ChatGPT 代码开源，防止大公司技术垄断。 |
| 688568 | 中科星图 | 2023-04-14 | 中科星图：中科星图股份有限公司2022年度利润分配及资本公积金转增股本方案的公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 同时，受高性能算力网络、人工智能大模型技术推动，空天信息泛在应用日趋普及，面向大众及大量中小企业的泛在需求将形成一片全新的增量空间 |
| 002122 | 天马股份 | 2023-04-18 | 天马股份：关于签署《投资合作协议》的自愿性信息披露公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 四、签署《投资合作协议》的目的及对公司的影响 1、目的 越来越多的中国公司参与通用大模型和垂直领域专业模型的研发势必对更大量的专业中文语义标注提出更多需求 |
| 300058 | 蓝色光标 | 2023-04-19 | 蓝色光标：2022年度财务决算报告 | priority_manual_event_candidate | AIGC;大模型 | AIGC | 7 | 同时「销博特」的多款 AIGC 产品「创意画廊」、销博特「创策图文」以及「萧助理」）为公司赋能的同时， |
| 603881 | 数据港 | 2023-04-19 | 数据港：上海数据港股份有限公司2022年年度股东大会会议资料 | priority_manual_event_candidate | ChatGPT;大模型 | GPT;大模型;AI大模型;ChatGPT | 7 | 尤其是近期 ChatGPT展示出的 AI大模型应用潜力，“开启 AI新纪元”令人感受到创新技术正从概念中逐步迈向生活化 |
| 300578 | 会畅通讯 | 2023-04-21 | 会畅通讯：关于2022年度计提资产减值准备和核销资产的公告 | priority_manual_event_candidate | AIGC | 大模型;AIGC | 7 | 也带来了全新的商业机会和客户体验革命的机会，公司经多方论证和评估，在平台升级的研发方向上考虑导入人工智能大模型技术，AIGC |
| 300081 | 恒信东方 | 2023-04-24 | 恒信东方：人工智能算力中心平台建设及运营项目可行性研究报告 | priority_manual_event_candidate | 大模型;大语言模型;模型备案;语言大模型 | 大模型;语言大模型;多模态大模型 | 6 | 按照应用场景划分，AI 大模型主要包括语言大模型、视觉大模型和多模态大模型等。 |
| 300291 | 百纳千成 | 2023-04-24 | 百纳千成：关于公司未弥补亏损达到实收股本总额三分之一的公告 | priority_manual_event_candidate | AIGC;ChatGPT;GPT;大模型;生成式AI | GPT;文心一言 | 7 | 近期 GPT-4、文心一言、Adobe Firefly、微软 Copilot 等一系列 AI 工具的不断推出以及后续版本的迭代升级 |
| 300366 | 创意信息 | 2023-04-24 | 创意信息：2022年年度财务报告 | priority_manual_event_candidate | 大模型;大语言模型;智谱;混元大模型;盘古大模型;语言大模型 | 大模型;盘古大模型 | 6 | 推动 MLOps AI 能力平台与鲲鹏、昇腾和盘古大模型的合作发展；二是围绕政务、能源、金融、运营商领域的国央企合作伙伴 |
| 688327 | 云从科技 | 2023-04-25 | 云从科技：关于向特定对象发行A股股票预案及相关文件修订情况说明的公告 | priority_manual_event_candidate | 大模型;模型备案 | 大模型 | 6 | ）》的修订内容 章节 章节内容 修订情况 三、本次募集资金投资项目的具体情况 （一）云从“行业精灵”大模型研发项目 |
| 688327 | 云从科技 | 2023-04-25 | 云从科技：2023年度向特定对象发行A股股票预案（修订稿） | priority_manual_event_candidate | ChatGPT;GPT;大模型;大语言模型;模型备案;生成式AI;语言大模型 | GPT | 6 | 一个预训练的语言表征模型，采用设计的自监督任务进行模型训练，训练好的模型通可应用于多个自然语言处理任务 GPT |
| 002065 | 东华软件 | 2023-04-26 | 东华软件：关于与腾讯云计算（北京）有限责任公司签署深化战略合作协议的公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 双方作为长期互信战略合作伙伴关系，均承诺在深化协议期内各自优势领域优先合作，包含双方自研矩阵的 AI 大模型 |
| 003005 | 竞业达 | 2023-04-26 | 竞业达：2023年度向特定对象发行A股股票预案 | priority_manual_event_candidate | AIGC;大模型;大语言模型;智谱;模型备案;混元大模型;语言大模型 | AIGC | 6 | 在教育行业方面，AIGC 具有广泛的应用前景。 |
| 300264 | 佳创视讯 | 2023-04-26 | 佳创视讯：关于未弥补亏损达到实收股本总额三分之一的公告 | priority_manual_event_candidate | AIGC | AIGC | 7 | 四款战略级新产品，为元宇宙内容生态建设提供产品服务体系，公司将在未来重点推动上述新产品的销售与市场合作机会，并结合AIGC |
| 603927 | 中科软 | 2023-04-26 | 中科软：中科软2022年年度股东大会会议资料 | priority_manual_event_candidate | AIGC;大模型;模型备案 | AIGC | 6 | 以行业应用软件领域知识（词根表、蓝图结构、样本程序等）进行专门训练，同时迁移通用 AI大平台能力，打造垂直领域 AIGC |
| 000925 | 众合科技 | 2023-04-27 | 众合科技：关于公司签署战略合作框架协议的公告 | priority_manual_event_candidate | 混元大模型 | 大模型;行业大模型 | 7 | ，沉淀行业知识和行业标准，驱动行业大模型训练；建立基于高效协作和时空大数据行业大模型下的新型城市信息模型总师服务能力 |
| 002354 | 天娱数科 | 2023-04-27 | 天娱数科：关于2022年年度业绩网上说明会召开情况的公告 | priority_manual_event_candidate | AIGC;ChatGPT;GPT;大语言模型;语言大模型 | GPT;大语言模型 | 7 | 平台接入GPT 等大语言模型，并通过海量数据资源针对不同场景进行调优，显著提升了虚拟世界中人、货、场互动中更高阶的理解 |
| 688262 | 国芯科技 | 2023-04-27 | 国芯科技：2022年度总经理工作报告 | priority_manual_event_candidate | ChatGPT;大模型;混元大模型 | GPT;ChatGPT | 6 | 从 ChatGPT 的功能实现上，可以看到数据是一切，是支撑云计算、智能AI业务落地迭代的基础和底层。 |
| 603108 | 润达医疗 | 2023-04-28 | 润达医疗：上海润达医疗科技股份有限公司2023年4月27日投资者交流会议记录 | priority_manual_event_candidate | GPT;大模型;智谱 | GPT | 7 | 未来随着 GPT 等新技术发展，公司也会进一步和国家数据中心研究机构合作，基于现有人工智能诊断模型进一步优化及开发 |
| 688343 | 云天励飞 | 2023-04-28 | 云天励飞：关于高级管理人员、核心技术人员离职的公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 |  王孝宇先生负责的工作均已完成交接，王孝宇先生辞任后，其原从事的研发工作由公司产品算法副总裁兼大模型筹备组组长肖嵘先生及公司研发团队承接 |
| 002230 | 科大讯飞 | 2023-05-05 | 科大讯飞：关于讯飞星火认知大模型成果发布会的提示性公告 | priority_manual_event_candidate | 大模型;大语言模型;星火认知;讯飞星火;语言大模型 | 大模型;星火认知;讯飞星火 | 7 | 本次发布会除了发布“讯飞星火认知大模型”技术成果之外，星火认知大模型在公司现有产品上的商业应用成果亦将同步发布 |
| 300192 | 科德教育 | 2023-05-05 | 科德教育：关于股价异常波动的公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 公司与合作方目前仅在职业教育领域进行合作，本身并不具备人工智能大模型相关技术，也不会因该技术给公司带来直接收入 |
| 688228 | 开普云 | 2023-05-05 | 开普云：开普云2022年年度股东大会会议资料 | priority_manual_event_candidate | AIGC;大模型;模型备案 | 大模型;AIGC | 7 | 2023 年公司将围绕 AIGC 战略，明确构建通用 AI技术与数据体系，不断精进行业 AI 大模型的产品能力 |
| 002712 | 思美传媒 | 2023-05-09 | 思美传媒：思美传媒股份有限公司关于签署战略合作协议的公告 | priority_manual_event_candidate | 大模型;大语言模型;智谱;语言大模型 | 智谱;大模型 | 7 | （以下简称“智谱大模型”）的商业化落地模式，并在智谱大模型的基础上训练并生成公司的专业化模型，在传媒及其他领域实现 |
| 605358 | 立昂微 | 2023-05-09 | 立昂微：立昂微2022年年度股东大会会议资料 | priority_manual_event_candidate | GPT | GPT | 6 | 芯片设计及封装测试等产业链环节、手机、消费电子、工业半导体、数据中心等应用领域的行情逐步恢复向好；特别是以 CHAT GPT |

## First Candidate Per Firm Examples

| sec_code | sec_name | announcement_date | announcement_title | candidate_tier | query_terms | matched_genai_terms | qian_recall_score | announcement_content |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300418 | 昆仑万维 | 2023-01-30 | 昆仑万维：2022年度业绩预告 | backfill_or_noisy_doc_with_action | AIGC;大模型 | AIGC | 6 | 的月活跃用户已超过2000万；海外社交娱乐平台Star X 降本增效增厚公司业绩，同时“昆仑天工”AIGC |
| 688039 | 当虹科技 | 2023-01-30 | 当虹科技：杭州当虹科技股份有限公司2022年年度业绩预告 | backfill_or_noisy_doc_with_action | AIGC | AIGC | 6 | 新行业布局以及产品持续创新需要，公司在视频处理核心算法、产品国产化替代、AR/VR/XR 技术、车载智能娱乐座舱以及AIGC |
| 000681 | 视觉中国 | 2023-01-31 | 视觉中国：股票交易异常波动公告 | strict_genai_context_without_action | AIGC | AIGC | 4 | 关于近期 A 股市场关注度较高的 AIGC（AI-Generated Content）相关概念情况，公司于 |
| 688787 | 海天瑞声 | 2023-02-06 | 海天瑞声：海天瑞声股票交易严重异常波动公告 | backfill_or_noisy_doc_with_action | ChatGPT;大模型;大语言模型;语言大模型 | GPT;ChatGPT | 6 | 截止本公告披露日，公司尚未与OpenAI开展合作，其ChatGPT的产品和服务尚未给公司带来业务收入。 |
| 300520 | 科大国创 | 2023-02-07 | 科大国创：股票交易异常波动公告 | backfill_or_noisy_doc_with_action | AIGC;ChatGPT;GPT;大模型 | GPT | 6 | 公司长期专注于数据智能技术的研发和应用，基于电信运营商客服、网络和运营调度等场景数据，应用BERT、GPT |
| 002229 | 鸿博股份 | 2023-02-08 | 鸿博股份：关于股价异动的公告 | priority_manual_event_candidate | AIGC | AIGC | 7 | 将智算中心打造成为具备标杆示范作用的 AI 产学研基地，也将与战略合作伙伴宣亚国际等就新华社元宇宙项目“山海中国”、以及 AIGC |
| 002722 | 物产金轮 | 2023-02-08 | 物产金轮：股票交易异常波动公告 | backfill_or_noisy_doc_with_action | AIGC;ChatGPT | GPT;AIGC;ChatGPT | 6 | 近日有投资者在深圳证券交易所互动易平台上询问公司参股公司北京灵伴即时智能科技有限公司（以下简称“灵伴科技”）关于 AIGC 和 ChatGPT |
| 601360 | 三六零 | 2023-02-08 | 三六零：三六零安全科技股份有限公司股票交易异常波动公告 | strict_genai_context_without_action | AIGC;ChatGPT;GPT | GPT;ChatGPT | 4 | 所形成的全部成果均仅作为公司内部自用的生产力工具使用，公司的类 ChatGPT 技术的各项指标只能达到略强于 GPT |
| 002362 | 汉王科技 | 2023-02-09 | 汉王科技：关于对汉王科技股份有限公司的关注函的回复公告 | backfill_or_noisy_doc_with_action | ChatGPT;大模型;大语言模型;智谱;语言大模型 | GPT;ChatGPT | 6 | 公司回复： NLP 技术是人工智能领域众多智能技术之一，现在讨论较多的ChatGPT大型通用模型研发与训练成本高昂 |
| 688416 | 恒烁股份 | 2023-02-13 | 恒烁股份：股票交易异常波动公告 | strict_genai_context_without_action | ChatGPT | GPT;ChatGPT | 4 | （三）媒体报道、市场传闻、热点概念 公司关注到，近期 ChatGPT、AI、算力等概念引起市场广泛热议 |
| 300785 | 值得买 | 2023-02-14 | 值得买：北京值得买科技股份有限公司与第一创业证券承销保荐有限责任公司关于北京值得买科技股份有限公司申请向不特定对象发行可转换公司债券的审核问询函的回复 | backfill_or_noisy_doc_with_action | AIGC;大模型;大语言模型;模型备案;语言大模型 | AIGC | 6 | 月底，淘宝已上线“直播未来城”，打造虚拟现实商业街；在内容生产领域，从 UGC 到 PGC再到现在的 AIGC |
| 000977 | 浪潮信息 | 2023-02-15 | 浪潮信息：股票交易异常波动公告 | backfill_or_noisy_doc_with_action | AIGC;ChatGPT;大模型;大语言模型;语言大模型 | GPT;大模型;AIGC;语言大模型;ChatGPT | 6 | 特别提示： 近日有投资者在深圳证券交易所互动易平台上询问公司关于 AIGC、ChatGPT和公司中文语言大模型 |
| 300250 | 初灵信息 | 2023-02-15 | 初灵信息：关于深圳证券交易所关注函的回复公告 | backfill_or_noisy_doc_with_action | AIGC;ChatGPT;大模型;大语言模型;智谱;混元大模型;腾讯混元;语言大模型 | GPT;ChatGPT | 6 | 3、公司的“智能对话平台”与 ChatGPT 技术没有关系，公司也没有涉及ChatGPT。 |
| 300364 | 中文在线 | 2023-02-15 | 中文在线：关于与北京澜舟科技有限公司签订战略合作协议的公告 | priority_manual_event_candidate | AIGC;ChatGPT;大模型;大语言模型;语言大模型 | GPT;ChatGPT | 7 | 近年来，澜舟科技在其享有自主知识产权的“孟子轻量化预训练模型”基础上，进一步融入了类ChatGPT的底层关键技术 |
| 600825 | 新华传媒 | 2023-02-16 | 新华传媒：股票交易异常波动公告 | strict_genai_context_without_action | ChatGPT | GPT;ChatGPT | 4 | 2 4、有媒体因公司参股中译语通科技股份有限公司（以下简称“中译语通”）而将公司列为“ChatGPT” |
| 300459 | 汤姆猫 | 2023-02-17 | 汤姆猫：股票交易异常波动公告 | strict_genai_context_without_action | AIGC;ChatGPT | GPT;ChatGPT | 4 | 二、公司关注并核实的情况说明 针对公司股票交易价格异常波动的情况，公司注意到市场近期 ChatGPT、 |
| 300476 | 胜宏科技 | 2023-02-20 | 胜宏科技：胜宏科技（惠州）股份有限公司关于对深圳证券交易所关注函的回复公告 | strict_genai_context_without_action | ChatGPT | GPT;ChatGPT | 4 | 长期来看，随着疫情影响的减缓，以及 ChatGPT 及人工智能、新能源汽车及智能驾驶等方面的需求驱动， |
| 688400 | 凌云光 | 2023-02-23 | 凌云光：关于确认2022年度及预计2023年度日常关联交易额度的公告 | strict_genai_context_without_action | 智谱 | 智谱 | 5 | 10 北京智谱华章科技有限公司 其他有限责任公司 刘德兵 1,480.6886 万元人民币 2019年 |
| 300033 | 同花顺 | 2023-02-27 | 同花顺：2022年年度报告摘要 | strict_genai_context_without_action | AIGC;大模型;大语言模型;混元大模型;语言大模型 | 大模型;AIGC | 3 | 自然语言处理、智能语音、图形图像识别与处理、数字人等关键技术攻关，特别是在 AI 大模型、AI 内容生成（AIGC |
| 300496 | 中科创达 | 2023-02-27 | 中科创达：2022年年度报告 | strict_genai_context_without_action | ChatGPT;大模型;大语言模型;智谱;模型备案;混元大模型;语言大模型 | GPT;大型语言模型;ChatGPT | 3 | 指 ChatGPT 是一个由 OpenAI 培训的大型语言模型，它使用了深度学习技术来理解和生成人类语言 |
| 601500 | 通用股份 | 2023-02-28 | 通用股份：江苏通用科技股份有限公司关于预计2023年度日常关联交易的公告 | strict_genai_context_without_action | 豆包 | 豆包 | 5 | （未经审计） (六) 无锡红豆包装装潢印刷有限公司 1、关联方基本情况 无锡红豆包装装潢印刷有限公司（ |
| 300654 | 世纪天鸿 | 2023-03-02 | 世纪天鸿：2022年年度报告 | strict_genai_context_without_action | AIGC;大模型;大语言模型;混元大模型;语言大模型 | AIGC | 4 | 世纪天鸿教育科技股份有限公司 2022 年年度报告全文 6 AIGC 指 AIGC（Artificial |
| 600050 | 中国联通 | 2023-03-08 | 中国联通：中国联合网络通信股份有限公司2022年年度报告摘要 | strict_genai_context_without_action | AIGC;智谱 | AIGC | 4 | 最近一段时间，元宇宙、数字孪生、AIGC（AI Generated Content，指利用人工智能技术生成内容 |
| 300561 | 汇金科技 | 2023-03-10 | 汇金科技：关于股票交易异常波动的公告 | backfill_or_noisy_doc_with_action | 大模型;大语言模型;语言大模型 | 大模型;文心一言 | 6 | 经公司核实现说明如下： 文心一言是百度基于文心大模型技术推出的生成式对话产品。 |
| 603881 | 数据港 | 2023-03-10 | 数据港：上海数据港股份有限公司2022年年度报告 | backfill_or_noisy_doc_with_action | AIGC;ChatGPT;大模型;模型备案;混元大模型;生成式AI | GPT;大模型;AI大模型;ChatGPT | 6 | 尤其是近期 ChatGPT展示出的 AI大模型应用潜力，“开启 AI新纪元”令人感受到创新技术正从概念中逐步迈向生活化 |
| 601138 | 工业富联 | 2023-03-14 | 工业富联：富士康工业互联网股份有限公司2022年年度报告摘要 | backfill_or_noisy_doc_with_action | AIGC;ChatGPT | GPT;ChatGPT | 6 | 客戶深化合作，推出新一代云计算基础设施解决方案，包括模块化服务器、高效运算（HPC）等，重点解决因 ChatGPT |
| 603186 | 华正新材 | 2023-03-14 | 华正新材：浙江华正新材料股份有限公司2022年年度报告 | backfill_or_noisy_doc_with_action | ChatGPT;大模型;大语言模型;模型备案;混元大模型;语言大模型 | GPT;ChatGPT | 6 | 全球数字化进程加速，再加上 ChatGPT等新兴 AI应用场景出现，服务器出货量持续高位。 |
| 301299 | 卓创资讯 | 2023-03-16 | 卓创资讯：2022年年度报告 | backfill_or_noisy_doc_with_action | ChatGPT;大模型;大语言模型;模型备案;混元大模型;语言大模型 | GPT;ChatGPT | 5 | 另外，以 5G、工业互联网、云计算、大数据、人工智能（如 ChatGPT）等技术的研发和应用为核心的数字经济 |
| 300058 | 蓝色光标 | 2023-03-17 | 蓝色光标：关于股票价格异常波动的公告 | strict_genai_context_without_action | AIGC;GPT | GPT;AIGC | 5 | 4、GPT-4与AIGC等相关AI技术尚处于起步阶段，对公司未来实际业务产生的收入存在不确定性。 |
| 300059 | 东方财富 | 2023-03-17 | 东方财富：东方财富信息股份有限公司2022年度董事会工作报告 | backfill_or_noisy_doc_with_action | AIGC | AIGC | 6 | 公司将不断加强 AI 能力建设，进一步强化自然语言处理、图像处理、语音识别和多模态融合技术能力，并继续深入 AIGC |
| 603135 | 中重科技 | 2023-03-19 | 中重科技：中重科技首次公开发行股票并在主板上市招股意向书 | strict_genai_context_without_action | Kimi;大模型;模型备案;混元大模型 | Kimi | 4 | 23 数控定梁龙门镗铣床 236.99 186.96 1 台 78.89% 24 数控卧式镗铣床 KiMi |
| 688018 | 乐鑫科技 | 2023-03-19 | 乐鑫科技：乐鑫科技2022年度企业社会责任报告 | strict_genai_context_without_action | ChatGPT | GPT;ChatGPT | 4 | 世界已经进⼊ AI 时代，我们⻅证了 ChatGPT 的⼀夜爆⽕，AI 技术同样也将成为 IoT 的关键驱动 |
| 300458 | 全志科技 | 2023-03-20 | 全志科技：2022年年度报告 | strict_genai_context_without_action | AIGC;ChatGPT;大模型;大语言模型;混元大模型;腾讯混元;语言大模型 | GPT;ChatGPT | 4 | to Digital Converter 模数转换器，把连续的模拟信号转变为离散的数字信号的器件 ChatGPT |
| 300556 | 丝路视觉 | 2023-03-20 | 丝路视觉：2022年年度报告 | backfill_or_noisy_doc_with_action | AIGC;GPT;大模型;混元大模型;腾讯混元 | GPT;AIGC | 6 | 一方面，技术将为创意设计者提供更高效的工作方式，比如 AIGC 和 Chat-GPT的发展与应用，在未来很有可能极大提高设计工作者的生产效率 |
| 300291 | 百纳千成 | 2023-03-21 | 百纳千成：股票交易异常波动公告 | backfill_or_noisy_doc_with_action | AIGC;ChatGPT;GPT | GPT;AIGC | 6 | 近期 GPT-4 的发布、众多大型企业的入局进一步发酵了市场对 AIGC 的关注与讨论，公司郑重提示广大投资者注意前沿技术在快速发展期所面临的技术研发不及预期 |
| 600228 | 返利科技 | 2023-03-21 | 返利科技：返利网数字科技股份有限公司股票交易异常波动公告 | strict_genai_context_without_action | AIGC;ChatGPT | GPT;ChatGPT | 4 |  公司现有导购等主营业务与 ChatGPT 等人工智能底层技术无关，公司不从事 ChatGPT 底层技术开发 |
| 601728 | 中国电信 | 2023-03-22 | 中国电信：中国电信股份有限公司2022年年度报告 | backfill_or_noisy_doc_with_action | 大模型;模型备案;混元大模型 | 大模型 | 6 | AI 核心能力强化自主研发，建成业内首个十亿参数量级城市治理领域的大模型，推动大模型向产业级模型库延展 |
| 603929 | 亚翔集成 | 2023-03-22 | 亚翔集成：亚翔集成-关于2022年度业绩说明会召开情况的公告 | backfill_or_noisy_doc_with_action | ChatGPT | GPT;ChatGPT | 5 | 13.随着 ai 人工智能的发展,科技界人士说这是第四次科技革命,随着opeai 的 chatgpt |
| 002463 | 沪电股份 | 2023-03-23 | 沪电股份：2022年度总经理工作报告 | priority_manual_event_candidate | ChatGPT;大模型;混元大模型 | GPT;ChatGPT | 7 | 近期OpenAI的ChatGPT的显著成功似乎为商业人工智能应用发展开启了新时代的大门，AI或将在未来 |
| 002803 | 吉宏股份 | 2023-03-23 | 吉宏股份：关于对深圳证券交易所关注函的回复公告-20230324 | backfill_or_noisy_doc_with_action | ChatGPT;大模型;大语言模型;语言大模型 | GPT;ChatGPT | 6 | 公司跨境电商业务在 2023 年 1 月接入 ChatGPT 的 API 接口，借助 ChatGPT |

## Priority First Candidate Per Firm Examples

| sec_code | sec_name | announcement_date | announcement_title | candidate_tier | query_terms | matched_genai_terms | qian_recall_score | announcement_content |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 002229 | 鸿博股份 | 2023-02-08 | 鸿博股份：关于股价异动的公告 | priority_manual_event_candidate | AIGC | AIGC | 7 | 将智算中心打造成为具备标杆示范作用的 AI 产学研基地，也将与战略合作伙伴宣亚国际等就新华社元宇宙项目“山海中国”、以及 AIGC |
| 300364 | 中文在线 | 2023-02-15 | 中文在线：关于与北京澜舟科技有限公司签订战略合作协议的公告 | priority_manual_event_candidate | AIGC;ChatGPT;大模型;大语言模型;语言大模型 | GPT;ChatGPT | 7 | 近年来，澜舟科技在其享有自主知识产权的“孟子轻量化预训练模型”基础上，进一步融入了类ChatGPT的底层关键技术 |
| 688039 | 当虹科技 | 2023-02-27 | 当虹科技：杭州当虹科技股份有限公司2022年度业绩快报公告 | priority_manual_event_candidate | AIGC | AIGC | 7 | 新行业布局以及产品持续创新需要，公司在视频处理核心算法、产品国产化替代、AR/VR/XR技术、车载智能娱乐座舱以及AIGC |
| 300418 | 昆仑万维 | 2023-02-28 | 昆仑万维：2022年度业绩快报 | priority_manual_event_candidate | AIGC;大模型 | AIGC | 7 | 本报告期，公司发布了“昆仑天工”AIGC全系列算法与模型，并宣布开源，用实际行动推动开源社区建设。 |
| 002463 | 沪电股份 | 2023-03-23 | 沪电股份：2022年度总经理工作报告 | priority_manual_event_candidate | ChatGPT;大模型;混元大模型 | GPT;ChatGPT | 7 | 近期OpenAI的ChatGPT的显著成功似乎为商业人工智能应用发展开启了新时代的大门，AI或将在未来 |
| 600522 | 中天科技 | 2023-03-23 | 中天科技：江苏中天科技股份有限公司关于召开终止分拆所属子公司上市事项投资者说明会召开情况的公告 | priority_manual_event_candidate | ChatGPT;大模型 | GPT;ChatGPT | 7 | /在 Al 时代，ChatGPT 的发展，对公司光纤光缆市场需求有无影响，是否要用更先进的产品来把计算撑大 |
| 002362 | 汉王科技 | 2023-03-24 | 汉王科技：2022年度总裁工作报告 | priority_manual_event_candidate | AIGC | AIGC | 6 | 业 务 模 式 和 体 系拓展数字经济、数字政府、数字社会各项业务RPA（机器人流程自动化）技术平台AIGC |
| 301185 | 鸥玛软件 | 2023-03-28 | 鸥玛软件：关于签署战略合作协议的公告 | priority_manual_event_candidate | ChatGPT | GPT;ChatGPT | 7 | ）交易双方 甲方：山东国家应用数学中心 乙方：山东山大鸥玛软件股份有限公司 （二）合作内容 1、类 ChatGPT |
| 688327 | 云从科技 | 2023-03-30 | 云从科技：第二届董事会第五次会议决议公告 | priority_manual_event_candidate | 大模型;模型备案 | 大模型 | 7 | 扣除发行费用后拟用于以下项目： 单位：万元 序号 项目名称 总投资额 拟使用募集资金额 1 云从“行业精灵”大模型研发项目 |
| 002015 | 协鑫能科 | 2023-04-02 | 协鑫能科：关于参与杭州星临科技有限责任公司增资扩股暨对外投资的公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 公司已在安徽签约建设百亿规模的液冷超级智算中⼼，为国产大模型的研发训练、各行业领域的“AI+”产业智能化升级 |
| 688568 | 中科星图 | 2023-04-14 | 中科星图：中科星图股份有限公司2022年度利润分配及资本公积金转增股本方案的公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 同时，受高性能算力网络、人工智能大模型技术推动，空天信息泛在应用日趋普及，面向大众及大量中小企业的泛在需求将形成一片全新的增量空间 |
| 002122 | 天马股份 | 2023-04-18 | 天马股份：关于签署《投资合作协议》的自愿性信息披露公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 四、签署《投资合作协议》的目的及对公司的影响 1、目的 越来越多的中国公司参与通用大模型和垂直领域专业模型的研发势必对更大量的专业中文语义标注提出更多需求 |
| 300058 | 蓝色光标 | 2023-04-19 | 蓝色光标：2022年度财务决算报告 | priority_manual_event_candidate | AIGC;大模型 | AIGC | 7 | 同时「销博特」的多款 AIGC 产品「创意画廊」、销博特「创策图文」以及「萧助理」）为公司赋能的同时， |
| 603881 | 数据港 | 2023-04-19 | 数据港：上海数据港股份有限公司2022年年度股东大会会议资料 | priority_manual_event_candidate | ChatGPT;大模型 | GPT;大模型;AI大模型;ChatGPT | 7 | 尤其是近期 ChatGPT展示出的 AI大模型应用潜力，“开启 AI新纪元”令人感受到创新技术正从概念中逐步迈向生活化 |
| 300578 | 会畅通讯 | 2023-04-21 | 会畅通讯：关于2022年度计提资产减值准备和核销资产的公告 | priority_manual_event_candidate | AIGC | 大模型;AIGC | 7 | 也带来了全新的商业机会和客户体验革命的机会，公司经多方论证和评估，在平台升级的研发方向上考虑导入人工智能大模型技术，AIGC |
| 300081 | 恒信东方 | 2023-04-24 | 恒信东方：人工智能算力中心平台建设及运营项目可行性研究报告 | priority_manual_event_candidate | 大模型;大语言模型;模型备案;语言大模型 | 大模型;语言大模型;多模态大模型 | 6 | 按照应用场景划分，AI 大模型主要包括语言大模型、视觉大模型和多模态大模型等。 |
| 300291 | 百纳千成 | 2023-04-24 | 百纳千成：关于公司未弥补亏损达到实收股本总额三分之一的公告 | priority_manual_event_candidate | AIGC;ChatGPT;GPT;大模型;生成式AI | GPT;文心一言 | 7 | 近期 GPT-4、文心一言、Adobe Firefly、微软 Copilot 等一系列 AI 工具的不断推出以及后续版本的迭代升级 |
| 300366 | 创意信息 | 2023-04-24 | 创意信息：2022年年度财务报告 | priority_manual_event_candidate | 大模型;大语言模型;智谱;混元大模型;盘古大模型;语言大模型 | 大模型;盘古大模型 | 6 | 推动 MLOps AI 能力平台与鲲鹏、昇腾和盘古大模型的合作发展；二是围绕政务、能源、金融、运营商领域的国央企合作伙伴 |
| 002065 | 东华软件 | 2023-04-26 | 东华软件：关于与腾讯云计算（北京）有限责任公司签署深化战略合作协议的公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 双方作为长期互信战略合作伙伴关系，均承诺在深化协议期内各自优势领域优先合作，包含双方自研矩阵的 AI 大模型 |
| 003005 | 竞业达 | 2023-04-26 | 竞业达：2023年度向特定对象发行A股股票预案 | priority_manual_event_candidate | AIGC;大模型;大语言模型;智谱;模型备案;混元大模型;语言大模型 | AIGC | 6 | 在教育行业方面，AIGC 具有广泛的应用前景。 |
| 300264 | 佳创视讯 | 2023-04-26 | 佳创视讯：关于未弥补亏损达到实收股本总额三分之一的公告 | priority_manual_event_candidate | AIGC | AIGC | 7 | 四款战略级新产品，为元宇宙内容生态建设提供产品服务体系，公司将在未来重点推动上述新产品的销售与市场合作机会，并结合AIGC |
| 603927 | 中科软 | 2023-04-26 | 中科软：中科软2022年年度股东大会会议资料 | priority_manual_event_candidate | AIGC;大模型;模型备案 | AIGC | 6 | 以行业应用软件领域知识（词根表、蓝图结构、样本程序等）进行专门训练，同时迁移通用 AI大平台能力，打造垂直领域 AIGC |
| 000925 | 众合科技 | 2023-04-27 | 众合科技：关于公司签署战略合作框架协议的公告 | priority_manual_event_candidate | 混元大模型 | 大模型;行业大模型 | 7 | ，沉淀行业知识和行业标准，驱动行业大模型训练；建立基于高效协作和时空大数据行业大模型下的新型城市信息模型总师服务能力 |
| 002354 | 天娱数科 | 2023-04-27 | 天娱数科：关于2022年年度业绩网上说明会召开情况的公告 | priority_manual_event_candidate | AIGC;ChatGPT;GPT;大语言模型;语言大模型 | GPT;大语言模型 | 7 | 平台接入GPT 等大语言模型，并通过海量数据资源针对不同场景进行调优，显著提升了虚拟世界中人、货、场互动中更高阶的理解 |
| 688262 | 国芯科技 | 2023-04-27 | 国芯科技：2022年度总经理工作报告 | priority_manual_event_candidate | ChatGPT;大模型;混元大模型 | GPT;ChatGPT | 6 | 从 ChatGPT 的功能实现上，可以看到数据是一切，是支撑云计算、智能AI业务落地迭代的基础和底层。 |
| 603108 | 润达医疗 | 2023-04-28 | 润达医疗：上海润达医疗科技股份有限公司2023年4月27日投资者交流会议记录 | priority_manual_event_candidate | GPT;大模型;智谱 | GPT | 7 | 未来随着 GPT 等新技术发展，公司也会进一步和国家数据中心研究机构合作，基于现有人工智能诊断模型进一步优化及开发 |
| 688343 | 云天励飞 | 2023-04-28 | 云天励飞：关于高级管理人员、核心技术人员离职的公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 |  王孝宇先生负责的工作均已完成交接，王孝宇先生辞任后，其原从事的研发工作由公司产品算法副总裁兼大模型筹备组组长肖嵘先生及公司研发团队承接 |
| 002230 | 科大讯飞 | 2023-05-05 | 科大讯飞：关于讯飞星火认知大模型成果发布会的提示性公告 | priority_manual_event_candidate | 大模型;大语言模型;星火认知;讯飞星火;语言大模型 | 大模型;星火认知;讯飞星火 | 7 | 本次发布会除了发布“讯飞星火认知大模型”技术成果之外，星火认知大模型在公司现有产品上的商业应用成果亦将同步发布 |
| 300192 | 科德教育 | 2023-05-05 | 科德教育：关于股价异常波动的公告 | priority_manual_event_candidate | 大模型 | 大模型 | 7 | 公司与合作方目前仅在职业教育领域进行合作，本身并不具备人工智能大模型相关技术，也不会因该技术给公司带来直接收入 |
| 688228 | 开普云 | 2023-05-05 | 开普云：开普云2022年年度股东大会会议资料 | priority_manual_event_candidate | AIGC;大模型;模型备案 | 大模型;AIGC | 7 | 2023 年公司将围绕 AIGC 战略，明确构建通用 AI技术与数据体系，不断精进行业 AI 大模型的产品能力 |
| 002712 | 思美传媒 | 2023-05-09 | 思美传媒：思美传媒股份有限公司关于签署战略合作协议的公告 | priority_manual_event_candidate | 大模型;大语言模型;智谱;语言大模型 | 智谱;大模型 | 7 | （以下简称“智谱大模型”）的商业化落地模式，并在智谱大模型的基础上训练并生成公司的专业化模型，在传媒及其他领域实现 |
| 605358 | 立昂微 | 2023-05-09 | 立昂微：立昂微2022年年度股东大会会议资料 | priority_manual_event_candidate | GPT | GPT | 6 | 芯片设计及封装测试等产业链环节、手机、消费电子、工业半导体、数据中心等应用领域的行情逐步恢复向好；特别是以 CHAT GPT |
| 603608 | 天创时尚 | 2023-05-10 | 天创时尚：天创时尚股份有限公司2022年年度股东大会会议资料 | priority_manual_event_candidate | AIGC;ChatGPT;生成式AI | GPT;ChatGPT | 7 | （3）全面推进 AI 人工智能在企业内部的应用： 随着人工智能 AI 技术如 chatGPT、生成式 |
| 603660 | 苏州科达 | 2023-05-10 | 苏州科达：2022年年度股东大会会议资料 | priority_manual_event_candidate | AIGC;ChatGPT | GPT;ChatGPT | 6 | 从 2022 年下半年开始，随着深度学习的发展，以 ChatGPT为代表的 AI应用的出现，标志着人工智能领域的重大突破 |
| 301380 | 挖金客 | 2023-05-11 | 挖金客：关于中证中小投资服务中心《股东质询函》的回复公告 | priority_manual_event_candidate | ChatGPT;大模型;大语言模型;语言大模型 | GPT;大语言模型;ChatGPT | 6 | 随着人工智能技术广泛应用，ChatGPT、文言一心等大语言模型系统推出，必然会为人机对话语音产品带来飞速发展 |
| 600728 | 佳都科技 | 2023-05-12 | 佳都科技：佳都科技2022年年度股东大会会议资料 | priority_manual_event_candidate | AIGC;ChatGPT;大模型;大语言模型;语言大模型 | 大模型 | 7 | ，公司在新一年将重点投入开发 AI 大模型技术与轨道交通、城市交通相结合的应用和解决方案。 |
| 688256 | 寒武纪 | 2023-05-12 | 寒武纪：2022年年度股东大会会议资料 | priority_manual_event_candidate | AIGC | AIGC | 7 | 另一方面，公司亦将把握 AIGC 产业下人工智能应用对智能算力的井喷需求，凭借公司领先的技术优势和当前产品的高度契合优势 |
| 300369 | 绿盟科技 | 2023-05-15 | 绿盟科技：2023年度向特定对象发行股票预案 | priority_manual_event_candidate | 大模型;大语言模型;智谱;模型备案;语言大模型 | 大模型 | 7 | 本项目拟在公司现有以安全大模型为代表的人工智能技术基础上，加强人才和人工智能基础设施的投入，构建满足网络安全行业应用的安全算力大脑平台 |
| 300520 | 科大国创 | 2023-05-15 | 科大国创：2023年度向特定对象发行股票预案 | priority_manual_event_candidate | ChatGPT;大模型;大语言模型;智谱;模型备案;语言大模型 | 大模型;行业大模型 | 6 | ，行业用户对软硬件产品和服务的智能化都提出了更高要求，以及随着近期各类通用大模型和行业大模型的推广和应用 |
| 688158 | 优刻得 | 2023-05-16 | 优刻得：优刻得2022年年度股东大会会议资料 | priority_manual_event_candidate | AIGC | AIGC | 6 | 在新兴的 AIGC等算力领域,构建集约化服务基座，复用客户存量基础设施，减少重复建设，为客户打造专属的一站式数字化解决方案 |

## Output Files

- `cninfo_fulltext_raw_query_hits.csv.gz`: one row per query hit before deduplication.
- `cninfo_fulltext_dedup_announcements.csv.gz`: deduplicated announcements with merged query terms.
- `cninfo_fulltext_a_share_announcements.csv.gz`: A-share formal disclosure rows.
- `cninfo_fulltext_candidate_pool.csv.gz`: ranked pool for later PDF download and manual coding.
- `manual_review_first_candidate_per_firm.csv`: first candidate per firm for Qian-style first-event screening.
- `manual_review_top3_candidates_per_firm.csv`: first three candidates per firm.
- `manual_review_priority_first_candidate_per_firm.csv`: first high-priority action candidate per firm.
- `manual_review_priority_top3_candidates_per_firm.csv`: first three high-priority action candidates per firm.
- `manual_review_priority_2023_2024_first_candidate_per_firm.csv`: high-priority first-candidate file for the Qian replication window.
- `manual_review_priority_2023_2024_top3_candidates_per_firm.csv`: first three high-priority candidates per firm for the Qian replication window.

## Interpretation

This source is large enough for a Qian-style funnel. The priority rows are not final treatment events. Manual coding must still verify that the listed company is the actor, the disclosure describes a concrete GenAI initiative, and the correct event date is the initiative date rather than a later annual-report or inquiry-reply date.
