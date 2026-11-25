# Acessibilidade (WCAG 2.1)

Resultado da auditoria de acessibilidade do frontend do **Estante** contra as diretrizes **WCAG 2.1, nível AA**, e o que foi corrigido.

## Sumário

- [Como a auditoria foi feita](#como-a-auditoria-foi-feita)
- [Contraste de cores](#contraste-de-cores)
- [Critérios verificados](#critérios-verificados)
- [Correções aplicadas](#correções-aplicadas)
- [Testes automatizados](#testes-automatizados)
- [O que a auditoria não cobre](#o-que-a-auditoria-não-cobre)

## Como a auditoria foi feita

1. **Cálculo de contraste** de cada par de cores do tema (`src/index.css`), com a fórmula de luminância relativa da WCAG.
2. **Testes automáticos com o axe-core** em 13 páginas renderizadas (início, login, cadastro, estante, detalhe da obra, cadastrar obra, perfil, editar perfil, listas, notificações, feed, recomendações e perfil público).
3. **Revisão manual da estrutura**: marcos (landmarks), títulos, rótulos de formulário, nomes acessíveis de botões, foco e navegação por teclado.

## Contraste de cores

Texto exige **4,5:1**; componentes de interface e ícones que carregam informação exigem **3:1**.

| Par | Razão | Situação |
| --- | --- | --- |
| Texto principal sobre o fundo creme | 11,1:1 | Atende |
| Texto secundário sobre o creme | 5,4:1 a 5,8:1 | Atende |
| Azul de destaque sobre o creme | 5,7:1 a 6,2:1 | Atende |
| Texto claro sobre o botão azul | 6,2:1 a 8,1:1 | Atende |
| Mensagem de erro sobre o creme | 5,3:1 a 5,7:1 | Atende |
| Texto de dica (placeholder) | 2,5:1 | **Falhava**, corrigido para 5,8:1 |
| Borda dos campos de formulário | 1,4:1 | **Falhava**, corrigida para 3,7:1 |
| Estrela de nota preenchida | 2,1:1 | **Falhava**, corrigida para 3,7:1 |
| Estrela de nota vazia (campo de avaliação) | 1,4:1 | **Falhava**, passou a ser contorno com 3,7:1 |

## Critérios verificados

| Critério | Situação | Como atende |
| --- | --- | --- |
| 1.1.1 Conteúdo não textual | Atende | Imagens decorativas têm `alt=""`; ícones têm `aria-hidden`; a nota em estrelas tem texto para leitores de tela ("4 de 5 estrelas") |
| 1.3.1 Informações e relações | Atende | Títulos em ordem, listas semânticas, rótulos ligados aos campos, `aside` com nome |
| 1.4.3 Contraste (mínimo) | Atende | Veja a tabela acima |
| 1.4.11 Contraste sem texto | Atende | Bordas de campos e estrelas com 3:1 ou mais |
| 2.1.1 Teclado | Atende | Tudo é alcançável por teclado; o menu da conta fecha com Esc |
| 2.4.1 Ignorar blocos | Atende | Link "Pular para o conteúdo" no início da página |
| 2.4.2 Página com título | Atende | O título da aba muda a cada página, por exemplo "Feed · Estante" |
| 2.4.3 Ordem do foco | Atende | Ao trocar de página, o foco vai para o conteúdo principal |
| 2.4.7 Foco visível | Atende | Contorno de 2 px em azul em todos os elementos focáveis |
| 3.1.1 Idioma da página | Atende | `lang="pt-BR"` |
| 3.3.1 e 3.3.2 Erros e rótulos | Atende | Campos com rótulo, erros ligados ao campo e mensagens com `role="alert"` |
| 4.1.2 Nome, função e valor | Atende | Botões de alternância com `aria-pressed`, notas com `role="radio"` e menu como navegação |
| 4.1.3 Mensagens de status | Atende | Erros e avisos usam `role="alert"`; o sino de notificações informa a quantidade de não lidas |
| 2.3.3 Animação | Atende | Animações e transições são desligadas com `prefers-reduced-motion` |

## Correções aplicadas

- **Pular para o conteúdo:** link visível ao receber o foco, apontando para o `main`.
- **Foco e título por página:** o `main` recebe o foco ao navegar e o título da aba reflete a página; obra, lista e perfil usam o próprio nome.
- **Menu da conta:** deixou de usar `role="menu"` sem navegação por setas e virou uma navegação com links; Esc fecha e devolve o foco ao botão.
- **Cores:** novos tokens `--color-line` (bordas de campos) e `--color-star` mais escuro; dicas dos campos sem transparência.
- **Estrelas de avaliação:** estrela vazia desenhada como contorno, para o estado não depender só da cor.
- **Marcos duplicados:** as duas áreas laterais do perfil ganharam nomes.
- **Movimento:** regra global para respeitar `prefers-reduced-motion`.

## Testes automatizados

```bash
cd frontend
npm test -- accessibility
```

O arquivo `src/integration/accessibility.test.tsx` roda o axe-core nas 13 páginas e confere o link de pular conteúdo, o título da aba, o foco ao trocar de página e o Esc no menu.

## O que a auditoria não cobre

- **Leitores de tela reais:** não foi feito teste manual com NVDA, VoiceOver ou TalkBack. O axe detecta problemas de estrutura, mas não mede a qualidade da experiência de quem usa um leitor.
- **Contraste no navegador:** o axe não mede contraste no ambiente de teste (jsdom); por isso a verificação é pelo cálculo da tabela acima.
- **Zoom e reflow:** 200% de zoom (1.4.4) e reflow em 320 px (1.4.10) não foram verificados em navegador real. O layout usa Tailwind responsivo, mas falta confirmar.
- **Imagens de terceiros:** avatar e capa vêm de links informados pelas pessoas e são tratados como decorativos.
- **Alvos de toque:** alguns botões pequenos (ícones de 16 px) ficam abaixo de 44 px; isso é recomendação da WCAG 2.2 e não está no nível AA da 2.1.
