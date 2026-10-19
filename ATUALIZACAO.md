# Versão 1.1.0 — preparação

As áreas passam a ser Administração das Eleições e Votação, Apuração e Totalização. Rotas, funções, IDs e autenticação foram preservados. Os checklists e referências do servidor permanecem íntegros.

A política central usa a 60ª Zona Eleitoral de Campo Novo do Parecis/MT, verifica a competência e exige conferir fontes oficiais a cada análise. Não implementa coleta periódica nem substituição automática do acervo remoto.

## Publicação

Integrar esta alteração e implantar o servidor pelo processo existente. Atualizar também a apresentação e as descrições das ferramentas no App proprietário: o editor do pacote de skills preserva esses campos do App conectado. Texto de descrição proposto: Manuais jurídicos eleitorais (AIJE, AIME, propaganda, candidatura, contas), Administração das Eleições e Votação, Apuração e Totalização. Referências TSE e TRE-MT.

A pasta plugin contém o pacote privado com a mesma conexão do App e instruções centrais. A apresentação original do App é preservada no manifesto de compatibilidade por ser administrada na origem. Não usar esse arquivo como substituto da atualização da apresentação no App.

Os manuais jurídicos são obtidos de servidor externo. Seus originais não foram regravados. A política orienta a interpretação e a nomenclatura das respostas. Documentos externos e metadados do App ainda podem exibir nomes antigos até a atualização na respectiva origem.

## Validação

Cinco testes existentes de autenticação, consulta e OpenAPI passaram localmente. Verificados os nomes retornados, as rotas e as referências operacionais preservadas. A implantação e o comportamento no host após reinstalação precisam de verificação.
