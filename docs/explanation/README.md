# Explanations

Background, context, and conceptual understanding of NHL Scrabble.

## What are explanations?

Explanations are **understanding-oriented** discussions that clarify and illuminate topics. They provide background, context, and discuss alternatives. Unlike tutorials (which teach) or how-to guides (which solve problems), explanations help you understand why things are the way they are.

## Available Explanations

### Core Concepts

- **[Why Scrabble Scoring?](why-scrabble-scoring.md)** - The rationale behind the project

  - Origin of the idea
  - Why it's interesting
  - What it demonstrates
  - Real-world applications

- **[How Scrabble Scoring Works](how-scrabble-scoring-works.md)** - Technical implementation details

  - Letter value calculations
  - Name parsing logic
  - Scoring algorithms
  - Special cases handling

- **[Architecture Overview](architecture.md)** - System design and structure

  - High-level architecture
  - Component responsibilities
  - Design decisions
  - Trade-offs made

- **[Web Architecture](web-architecture.md)** - Web interface design

  - FastAPI integration
  - Frontend architecture
  - API endpoints
  - Real-time features

### Technical Decisions

- **[NHL API Strategy](nhl-api-strategy.md)** - How we integrate with NHL's API

  - Why this API over alternatives
  - Rate limiting approach
  - Caching strategy
  - Error handling philosophy

- **[Testing Philosophy](testing-philosophy.md)** - Our approach to testing

  - Why we test what we test
  - Unit vs integration vs end-to-end
  - Coverage targets
  - Mocking strategies

### Development Tools

- **[UV Ecosystem](../../UV-ECOSYSTEM.md)** - Why and how we use UV

  - Benefits of UV (10-100x speedup)
  - Integration with tox
  - Performance improvements
  - Migration from pip/poetry

## How to use explanations

- **Build understanding**: Read to understand the "why" behind decisions
- **Evaluate alternatives**: See what was considered and why
- **Learn patterns**: Understand approaches applicable to other projects
- **Contribute effectively**: Know the philosophy before proposing changes

## Not finding what you need?

- **Learning the basics?** Start with [Tutorials](../tutorials/)
- **Solving a problem?** Check [How-to Guides](../how-to/)
- **Looking up syntax?** See [Reference](../reference/) documentation
- **Have a question?** See our [Support Guide](../../SUPPORT.md)
- **Want to discuss?** [Start a discussion](https://github.com/bdperkin/nhl-scrabble/discussions)

## Contributing

Have insights to share about why the project is designed the way it is? We welcome explanatory documentation!

See [How to Contribute](../how-to/contribute-code.md) to add new explanations.
