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

- **[Architecture Overview](architecture.md)** - System design and structure

  - High-level architecture
  - Component responsibilities
  - Design decisions
  - Trade-offs made

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

- **[UV Ecosystem](uv-ecosystem.md)** - Why and how we use UV

  - Benefits of UV
  - Integration with tox
  - Performance improvements
  - Migration from pip

### Development Practices

- **[Development Workflow](development-workflow.md)** - How we work on the project

  - Branch workflow
  - PR process
  - Review standards
  - Release process

- **[Report System Architecture](report-system.md)** - How reports work

  - Report generator design
  - Plugin architecture
  - Extensibility
  - Future plans

- **[Type Safety Approach](type-safety.md)** - Why we use type hints

  - Benefits of type safety
  - MyPy strict mode
  - Pydantic for data
  - Gradual typing approach

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
