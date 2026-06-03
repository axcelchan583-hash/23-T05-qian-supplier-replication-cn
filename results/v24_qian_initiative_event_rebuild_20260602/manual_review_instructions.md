# Qian-Style GenAI Initiative Manual Review

Code the company-side disclosure, not the investor question alone.

`manual_keep_qian_0_1 = 1` only if all conditions hold:

1. The focal listed company is the actor or direct adopter.
2. The text explicitly refers to a strict GenAI technology, such as ChatGPT, GPT, AIGC, DeepSeek, large language models, generative AI, or a named large-model platform.
3. The disclosure contains a specific initiative: investment, adoption, product integration, product launch, deployment, procurement, contract, pilot, commercialization, or workflow incorporation.
4. The event date/source is verifiable from the disclosure record.

Set `manual_keep_qian_0_1 = 0` for:

- denial/no-current-business answers;
- pure investor-question triggers where the company does not affirm an initiative;
- attention/exploration boilerplate, including "密切关注" and "以公告为准";
- generic AI, RAG, Agent, NLP, algorithm, or intelligent-manufacturing mentions without strict GenAI initiative evidence;
- broad industry trend discussion where the company is not taking a concrete action.

`manual_product_or_process`:

- `product`: GenAI is integrated into products, services, customer-facing features, or external offerings.
- `process`: GenAI is mainly used in internal workflow, production, R&D, customer service, office, or operations.
- `both`, `unclear`, or blank are allowed during first-pass review.

Recommended order:

1. Review `manual_review_v23_upstream_focal_events.csv` first to audit the contaminated v23 treatment.
2. Review `manual_review_first_supplier_linked_auto_candidate_per_firm.csv` as the Qian-style first-pass treatment queue.
3. Use `manual_review_supplier_linked_candidate_events.csv` to recover an alternative earlier/later event if the first machine candidate is rejected.
4. Use `manual_review_qian_candidate_events.csv` only for broader event-library backtracking.
5. After manual labels are complete, rerun supplier AR only on the first kept event per focal firm.
