# Manutenção do perfil

O README exibe textos, ícones locais, banner e painéis. Não exige instalação de programas para visitantes ou para manter o perfil.

## Bio lateral (configuração da conta, fora do README)

Nome: Gustavo Brandão Gimenez

Bio: Supervisor de suporte técnico na UCDB, com foco em infraestrutura de redes. Professor universitário na Unigran Capital.

Abra seu perfil, escolha **Edit profile**, substitua a bio e salve. Preserve os demais campos.

## Atualizações

A automação **Atualizar perfil** roda diariamente às 09:23 UTC (05:23 em Cuiabá) e pode ser executada em **Actions → Atualizar perfil → Run workflow**. Os horários agendados podem sofrer atrasos do GitHub.

O segredo existente `WAKATIME_API_KEY` é reutilizado. Se os tempos não atualizarem, configure nele um token pessoal OAuth de leitura do WakaTime conforme https://wakatime.com/developers#authentication. Nunca coloque a credencial no README ou em um arquivo do repositório. O painel mostra apenas agregados de linguagens, sem caminhos, nomes de projetos ou máquinas.

Pac-Man usa as contribuições reais da conta. As alternativas sem movimento respeitam a preferência de reduzir animações do navegador. O WakaTime mostra a data da última coleta e preserva os dados anteriores em falhas de conexão. As porcentagens vêm do WakaTime; categorias com menos de um minuto e Binary/Other são omitidas, portanto as linhas visíveis podem não somar 100%.

## Arquivos

- `assets/banner.png`: arte-base autoral gerada com IA a partir do conceito aprovado.
- `assets/banner.svg`: arte incorporada com cursor e reflexo azul animados.
- `assets/icons/`: fontes locais dos ícones de tecnologias e contatos.
- `scripts/build_assets.py`: recria banner e ícones visuais sem bibliotecas externas.
- `scripts/update_wakatime.py`: atualiza o painel e a alternativa em texto.
- `scripts/prepare_pacman.py`: aplica a paleta e gera a versão sem animações.

Para reconstruir os arquivos visuais localmente: `python scripts/build_assets.py`. O banner estático é mantido para quem usa redução de movimento.

Sugestão de repositórios fixados: landing-karina-ramai, calculadora-csharp e clone-tabnews. Fixá-los é uma configuração independente do README.
