# ecom-agent

An agent-based ecommerce project built around **SaborMix**, a fictional kitchen robot brand. It showcases how a conversational AI agent can handle end-to-end customer interactions for an ecommerce business.

## What it does

The agent supports conversations with customers across three main areas:

- **Sales and marketing** — presents and recommends SaborMix products (Essential and ProConnect models), handles pricing, payment options, shipping and returns.
- **Recipes** — guides customers through recipes designed for their SaborMix device, with model-specific instructions and settings.
- **Technical support** — helps troubleshoot common issues and, when needed, initiates the repair and warranty process.

## Project structure

```
SaborMIx/
├── products/        # Product sheets (ES + EN)
├── recipes/         # Step-by-step recipes (ES + EN)
└── support/         # Troubleshooting and sales dossier (ES + EN)
```

Each area contains language-specific folders (`es/` and `en/`) with markdown knowledge files the agent uses as its knowledge base.
