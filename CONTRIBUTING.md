# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o DJE Análise v2! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Como Contribuir

### 1. Reportar Bugs

Se você encontrou um bug, por favor:

1. Verifique se o bug já não foi reportado nas [Issues](https://github.com/brenobbbenicio-blip/dje-analise-v2/issues)
2. Abra uma nova issue com:
   - Título descritivo
   - Descrição detalhada do problema
   - Passos para reproduzir o bug
   - Comportamento esperado vs observado
   - Informações do ambiente (OS, versão Python, etc.)
   - Screenshots se aplicável

### 2. Sugerir Melhorias

Para sugerir novas funcionalidades:

1. Abra uma issue com a tag `enhancement`
2. Descreva claramente a funcionalidade desejada
3. Explique por que ela seria útil para o projeto
4. Proponha uma possível implementação

### 3. Submeter Pull Requests

#### Preparação

1. **Fork o repositório**
   ```bash
   # Clique em "Fork" no GitHub
   git clone https://github.com/seu-usuario/dje-analise-v2.git
   cd dje-analise-v2
   ```

2. **Configure o upstream**
   ```bash
   git remote add upstream https://github.com/brenobbbenicio-blip/dje-analise-v2.git
   ```

3. **Crie uma branch para sua feature**
   ```bash
   git checkout -b feature/nome-da-feature
   # ou
   git checkout -b fix/nome-do-bug
   ```

#### Desenvolvimento

1. **Faça suas alterações**
   - Siga o estilo de código do projeto
   - Adicione testes se aplicável
   - Atualize a documentação se necessário

2. **Teste suas alterações**
   ```bash
   # Execute os testes
   pytest tests/

   # Verifique o linting
   black src/
   flake8 src/
   ```

3. **Commit suas mudanças**
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade X"
   ```

   **Convenção de commits:**
   - `feat:` nova funcionalidade
   - `fix:` correção de bug
   - `docs:` alteração em documentação
   - `refactor:` refatoração de código
   - `test:` adição/alteração de testes
   - `chore:` tarefas de manutenção

#### Submissão

1. **Push para seu fork**
   ```bash
   git push origin feature/nome-da-feature
   ```

2. **Abra um Pull Request**
   - Acesse seu fork no GitHub
   - Clique em "New Pull Request"
   - Preencha o template com:
     - Descrição das mudanças
     - Issue relacionada (se houver)
     - Screenshots (se aplicável)
     - Checklist de verificação

3. **Aguarde review**
   - Mantenha o PR atualizado com a branch main
   - Responda aos comentários dos revisores
   - Faça ajustes se solicitado

## 🎨 Padrões de Código

### Python

- Siga [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) para formatação
- Máximo de 88 caracteres por linha
- Use type hints quando possível
- Docstrings no formato Google

**Exemplo:**
```python
def process_document(text: str, max_length: int = 1000) -> Dict[str, Any]:
    """
    Processa um documento de jurisprudência.

    Args:
        text: Texto do documento
        max_length: Comprimento máximo do chunk

    Returns:
        Dicionário com documento processado

    Raises:
        ValueError: Se o texto estiver vazio
    """
    pass
```

### Estrutura de Arquivos

- Módulos em `src/`
- Testes em `tests/`
- Documentação em `docs/`
- Exemplos em `examples/`

### Testes

- Use pytest
- Cobertura mínima de 80%
- Testes unitários para funções críticas
- Testes de integração para fluxos completos

## 📝 Documentação

- Atualize o README.md se adicionar funcionalidades
- Documente funções complexas
- Adicione exemplos de uso
- Mantenha comentários claros e concisos

## 🔍 Checklist do Pull Request

Antes de submeter, verifique:

- [ ] Código segue os padrões do projeto
- [ ] Testes foram adicionados/atualizados
- [ ] Todos os testes passam
- [ ] Documentação foi atualizada
- [ ] Commit messages são descritivas
- [ ] Não há conflitos com a branch main
- [ ] Código não adiciona novas dependências sem justificativa

## 🚫 O Que Evitar

- Commits diretamente na branch main
- Pull Requests muito grandes (divida em partes menores)
- Mudanças não relacionadas no mesmo PR
- Código sem testes
- Breaking changes sem discussão prévia
- Adicionar dependências desnecessárias

## 💡 Ideias de Contribuição

Procurando por onde começar? Aqui estão algumas ideias:

### Para Iniciantes
- Melhorar documentação
- Adicionar exemplos de uso
- Corrigir typos
- Traduzir documentação

### Intermediário
- Adicionar testes
- Melhorar tratamento de erros
- Otimizar performance
- Implementar logging

### Avançado
- Implementar scraper real do TSE
- Adicionar suporte a outros embeddings
- Criar interface web
- Adicionar cache de consultas
- Implementar análise de sentimento
- Adicionar exportação de relatórios

## 📞 Dúvidas?

Se você tiver dúvidas sobre como contribuir:

- Abra uma issue com a tag `question`
- Entre em contato através das issues do GitHub
- Consulte a documentação do projeto

## 🎉 Reconhecimento

Todos os contribuidores serão reconhecidos no README.md e no histórico de commits do projeto.

Agradecemos sua contribuição! 🙏
