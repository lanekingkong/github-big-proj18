# Contributing to UAMP

First off, thank you for considering contributing to UAMP! It's people like you that make UAMP such a great tool for the AI development community.

## 📋 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@uamp.dev.

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm 8+ or yarn 1.22+
- Git

### Development Setup
1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/UAMP.git
   cd UAMP
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/lanekingkong/UAMP.git
   ```
4. **Install dependencies**:
   ```bash
   npm install
   ```
5. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
6. **Start development server**:
   ```bash
   npm run dev
   ```

## 🎯 How Can I Contribute?

### Reporting Bugs
Before creating bug reports, please check the [existing issues](https://github.com/lanekingkong/UAMP/issues) to see if the problem has already been reported.

**How to submit a good bug report:**
1. **Use a clear and descriptive title**
2. **Describe the exact steps to reproduce the problem**
3. **Provide specific examples** (code snippets, screenshots, etc.)
4. **Describe the expected behavior**
5. **Include environment details**:
   - OS and version
   - Node.js version
   - UAMP version
   - AI tools being used

### Suggesting Enhancements
Enhancement suggestions are tracked as [GitHub issues](https://github.com/lanekingkong/UAMP/issues).

**How to submit a good enhancement suggestion:**
1. **Use a clear and descriptive title**
2. **Provide a step-by-step description** of the suggested enhancement
3. **Explain why this enhancement would be useful** to most UAMP users
4. **List any similar features** in other tools
5. **Specify which version of UAMP you're using**

### Pull Requests

#### Process
1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/amazing-feature
   # or
   git checkout -b fix/annoying-bug
   ```
2. **Make your changes** following our coding standards
3. **Write or update tests** as needed
4. **Run the test suite** to ensure nothing is broken:
   ```bash
   npm test
   ```
5. **Update documentation** if needed
6. **Commit your changes** using conventional commits:
   ```bash
   git commit -m "feat: add amazing new feature"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open a Pull Request** against the `main` branch

#### Pull Request Guidelines
- **Keep PRs focused**: One feature/bug fix per PR
- **Update documentation**: Include updates to README, docs, or comments
- **Add tests**: New features should include tests
- **Follow the template**: Use the provided PR template
- **Link issues**: Reference related issues in the PR description

## 💻 Development Guidelines

### Code Standards

#### JavaScript/TypeScript
- Use **TypeScript** for all new code
- Follow the **Airbnb JavaScript Style Guide**
- Use **ESLint** and **Prettier** for code formatting
- Maximum line length: **100 characters**

```typescript
// Good example
interface UserContext {
  id: string;
  name: string;
  preferences: UserPreferences;
}

function processContext(context: UserContext): ProcessedContext {
  // Function implementation
}

// Bad example
function proc(ctx) {
  // Unclear variable names, no types
}
```

#### File Structure
```
src/
├── core/           # Core business logic
├── plugins/        # Tool integrations
├── api/           # API endpoints
├── ui/            # User interface
├── utils/         # Utility functions
└── types/         # TypeScript definitions
```

#### Naming Conventions
- **Files**: kebab-case (e.g., `memory-graph.ts`)
- **Variables**: camelCase (e.g., `userContext`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_CONTEXT_SIZE`)
- **Classes**: PascalCase (e.g., `MemoryGraph`)
- **Interfaces**: PascalCase (e.g., `IContext`)
- **Types**: PascalCase with "Type" suffix (e.g., `ContextType`)

### Testing

#### Test Structure
```typescript
describe('MemoryGraph', () => {
  describe('addContext()', () => {
    it('should add context to graph', async () => {
      // Arrange
      const graph = new MemoryGraph();
      const context = createTestContext();
      
      // Act
      const result = await graph.addContext(context);
      
      // Assert
      expect(result.id).toBeDefined();
      expect(graph.size).toBe(1);
    });
    
    it('should generate embeddings for new context', async () => {
      // Test embedding generation
    });
  });
});
```

#### Test Coverage Requirements
- **Unit tests**: >90% coverage
- **Integration tests**: Critical paths only
- **E2E tests**: Major user workflows

### Documentation

#### Code Comments
```typescript
/**
 * Adds a new context to the memory graph.
 * 
 * @param context - The context to add
 * @returns Promise resolving to the created memory node
 * @throws {ValidationError} If context is invalid
 * @example
 * const node = await graph.addContext({
 *   content: 'API design discussion',
 *   tool: 'claude-code'
 * });
 */
async addContext(context: Context): Promise<MemoryNode> {
  // Implementation
}
```

#### README Updates
- Update README.md for user-facing changes
- Add examples for new features
- Update installation instructions if needed

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(plugins): add VS Code extension support
fix(memory): handle empty context in graph
docs(readme): update installation instructions
```

## 🧪 Testing Locally

### Running Tests
```bash
# Run all tests
npm test

# Run specific test file
npm test -- --testPathPattern=memory-graph

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

### Testing Plugins
```bash
# Test specific plugin
cd plugins/claude-code
npm test

# Test all plugins
npm run test:plugins
```

## 🔧 Building and Packaging

### Development Build
```bash
npm run build:dev
```

### Production Build
```bash
npm run build
```

### Creating Distribution Packages
```bash
# Create platform-specific packages
npm run package:win    # Windows
npm run package:mac    # macOS
npm run package:linux  # Linux
```

## 📦 Plugin Development

### Creating a New Plugin
1. **Use the plugin template**:
   ```bash
   cp -r plugins/template plugins/my-new-tool
   ```
2. **Update plugin metadata** in `manifest.json`
3. **Implement the plugin interface**
4. **Add tests** for your plugin
5. **Update plugin documentation**

### Plugin Structure
```
plugins/my-tool/
├── index.ts           # Main plugin implementation
├── manifest.json      # Plugin metadata
├── README.md          # Plugin documentation
├── package.json       # Dependencies
├── tests/             # Plugin tests
└── assets/            # Plugin assets
```

## 🐛 Debugging

### VS Code Debug Configuration
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug UAMP",
      "program": "${workspaceFolder}/src/index.ts",
      "outFiles": ["${workspaceFolder}/dist/**/*.js"]
    }
  ]
}
```

### Common Debug Commands
```bash
# Debug with Node inspector
npm run debug

# Check memory usage
npm run profile:memory

# Check CPU usage
npm run profile:cpu
```

## 📈 Performance Testing

### Load Testing
```bash
# Run load test
npm run test:load

# Generate performance report
npm run perf:report
```

### Benchmarking
```bash
# Run benchmarks
npm run benchmark

# Compare with previous version
npm run benchmark:compare
```

## 🔍 Code Review Process

### What We Look For
1. **Code quality**: Readability, maintainability, performance
2. **Test coverage**: Adequate tests for new functionality
3. **Documentation**: Updated docs and comments
4. **Security**: No security vulnerabilities
5. **Performance**: No performance regressions

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Security considerations addressed
- [ ] Performance impact considered

## 🏆 Recognition

### Contributor Levels
- **New Contributor**: First merged PR
- **Active Contributor**: 5+ merged PRs
- **Core Contributor**: 20+ merged PRs, deep system knowledge
- **Maintainer**: Invitation to join maintainer team

### Recognition Methods
- **Contributor Hall of Fame** in README
- **Special thanks** in release notes
- **Swag** for significant contributions
- **Conference speaking opportunities**

## ❓ Frequently Asked Questions

### How do I get help?
- **Documentation**: Check the [docs](docs/) first
- **Discord**: Join our [Discord community](https://discord.gg/uamp)
- **Issues**: Search existing issues
- **Stack Overflow**: Use the `uamp` tag

### How are decisions made?
- **Technical decisions**: RFC process for major changes
- **Feature prioritization**: Community voting + maintainer input
- **Breaking changes**: Major version releases with migration guides

### Can I contribute to documentation?
Absolutely! Documentation contributions are highly valued. See the [docs/](docs/) directory for existing documentation.

## 📝 Additional Resources

- [Project Roadmap](ROADMAP.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [API Reference](docs/api-reference.md)
- [Plugin Development Guide](docs/plugin-development.md)
- [Security Guidelines](SECURITY.md)

---

Thank you for contributing to UAMP! Together, we're building the future of AI development tools. 🚀