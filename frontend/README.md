# Frontend · Estante

Interface web do projeto, feita com **React 19 + TypeScript + Vite + Tailwind 4**, em estilo minimalista (creme e azul de tom quente).

## Como executar

```bash
cp .env.example .env     # VITE_API_URL=http://localhost:8000
npm install
npm run dev              # http://localhost:5173
```

O backend precisa estar rodando — veja o [Manual de Execução](../docs/MANUAL_EXECUCAO.md).

| Script | O que faz |
| --- | --- |
| `npm run dev` | Servidor de desenvolvimento com HMR |
| `npm run build` | Checagem de tipos (`tsc`) + build de produção |
| `npm run lint` | Lint com oxlint |

## Telas

| Rota | Página | Acesso |
| --- | --- | --- |
| `/` | `HomePage` | Público |
| `/login` | `LoginPage` | Público |
| `/cadastro` | `RegisterPage` | Público |
| `/livros` | `CatalogPage` | Público |
| `/livros/:id` | `BookDetailPage` | Público |
| `/livros/novo` | `BookFormPage` | 🔒 Logado |
| `/listas` | `ListsPage` | 🔒 Logado |
| `/listas/:id` | `ListDetailPage` | 🔒 Logado |

## Estrutura

```text
src/
├── pages/        # Uma tela por arquivo
├── components/   # Layout, Navbar, BookCard e primitivos de UI
├── auth/         # AuthContext (sessão JWT) e ProtectedRoute
└── lib/          # Cliente HTTP (api.ts), tipos e helpers
```

## Tema

As cores e fontes ficam em `src/index.css`, dentro de `@theme`, e viram classes do Tailwind (`bg-cream-100`, `text-blue-warm-600`, `font-serif`…).

| Token | Cor | Uso |
| --- | --- | --- |
| `cream-100` | `#FAF5EA` | Fundo da página |
| `cream-50` | `#FDFAF3` | Cartões e campos |
| `blue-warm-600` | `#3A5F8A` | Ações e destaques |
| `ink` | `#3A3027` | Texto |
