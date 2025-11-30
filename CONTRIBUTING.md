# Guia de Contribuição

Obrigado por considerar contribuir com o DJE Análise v2! Este documento fornece diretrizes para contribuições.

## Como Contribuir

### Reportar Bugs

Se você encontrou um bug:

1. Verifique se o bug já foi reportado nas [Issues](https://github.com/brenobbbenicio-blip/dje-analise-v2/issues)
2. Se não, crie uma nova issue com:
   - Título claro e descritivo
   - Descrição detalhada do problema
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Screenshots (se aplicável)
   - Ambiente (OS, Python version, etc.)

### Sugerir Melhorias

Para sugerir uma nova funcionalidade:

1. Abra uma issue com o prefixo `[FEATURE]`
2. Descreva a funcionalidade desejada
3. Explique por que seria útil
4. Considere possíveis implementações

### Pull Requests

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Faça suas alterações
4. Execute os testes: `pytest`
5. Execute o linting: `black src/` e `flake8 src/`
6. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
7. Push para a branch (`git push origin feature/MinhaFeature`)
8. Abra um Pull Request

### Padrões de Código

- Siga PEP 8
- Use Black para formatação
- Máximo 127 caracteres por linha
- Use type hints
- Docstrings em português para funções públicas
- Nomes de variáveis e funções em inglês

### Padrões de Commit

Use mensagens de commit claras:

```
Add: Nova funcionalidade
Fix: Correção de bug
Update: Atualização de código existente
Refactor: Refatoração
Docs: Documentação
Test: Testes
```

### Testes

- Adicione testes para novas funcionalidades
- Mantenha cobertura de testes > 80%
- Execute `pytest` antes de fazer commit
- Use fixtures para dados de teste

### Documentação

- Atualize o README.md se necessário
- Adicione docstrings em funções novas
- Comente código complexo
- Atualize exemplos se a API mudar

## Configuração do Ambiente de Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/brenobbbenicio-blip/dje-analise-v2.git
cd dje-analise-v2

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Execute testes
pytest

# Execute linting
black src/
flake8 src/
```

## Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros

## Dúvidas?

Se tiver dúvidas, abra uma issue com o prefixo `[QUESTION]`.

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a licença MIT.
