"""
Documentos de exemplo para cada tribunal eleitoral
"""

TRE_EXAMPLE_DOCUMENTS = {
    "TSE": [
        {
            'title': 'Acórdão TSE 123.456 - Registro de Candidatura',
            'text': """RECURSO ESPECIAL ELEITORAL. REGISTRO DE CANDIDATURA. REQUISITOS LEGAIS.
            O registro de candidatura deve atender aos requisitos previstos na Lei nº 9.504/97,
            incluindo filiação partidária prévia, domicílio eleitoral e demais condições de
            elegibilidade. A ausência de qualquer destes requisitos implica no indeferimento
            do registro. Recurso conhecido e provido.""",
            'metadata': {
                'number': '123.456',
                'year': 2023,
                'type': 'Acórdão',
                'tema': 'Registro de Candidatura'
            }
        },
        {
            'title': 'Acórdão TSE 789.012 - Propaganda Eleitoral',
            'text': """REPRESENTAÇÃO. PROPAGANDA ELEITORAL IRREGULAR. INTERNET.
            A propaganda eleitoral na internet deve observar os limites legais estabelecidos
            pela Lei das Eleições. A veiculação de conteúdo difamatório ou inverídico configura
            abuso de direito e pode ensejar aplicação de multa e remoção do conteúdo.
            Representação julgada procedente.""",
            'metadata': {
                'number': '789.012',
                'year': 2023,
                'type': 'Acórdão',
                'tema': 'Propaganda Eleitoral'
            }
        },
    ],
    "TRE-MG": [
        {
            'title': 'Acórdão TRE-MG 45.123 - Eleições Municipais BH',
            'text': """RECURSO ELEITORAL. ELEIÇÕES MUNICIPAIS. BELO HORIZONTE.
            O candidato deve comprovar domicílio eleitoral no município há pelo menos um ano
            antes do pleito. A comprovação de residência em Minas Gerais é requisito essencial
            para candidatura a cargos municipais. No caso em análise, o recorrente apresentou
            documentação suficiente demonstrando vínculo com o estado de Minas Gerais.
            Recurso provido para deferir o registro.""",
            'metadata': {
                'number': '45.123',
                'year': 2023,
                'type': 'Acórdão',
                'tema': 'Registro de Candidatura',
                'city': 'Belo Horizonte'
            }
        },
        {
            'title': 'Acórdão TRE-MG 56.789 - Prestação de Contas Uberlândia',
            'text': """PRESTAÇÃO DE CONTAS. ELEIÇÕES 2022. UBERLÂNDIA/MG.
            A prestação de contas deve ser apresentada no prazo legal, contendo todos os
            documentos comprobatórios das receitas e despesas de campanha. Verificada
            irregularidade na contabilização de despesas, deve ser oportunizada a
            retificação. Contas aprovadas com ressalvas.""",
            'metadata': {
                'number': '56.789',
                'year': 2022,
                'type': 'Acórdão',
                'tema': 'Prestação de Contas',
                'city': 'Uberlândia'
            }
        },
    ],
    "TRE-RJ": [
        {
            'title': 'Acórdão TRE-RJ 78.234 - Propaganda Rio de Janeiro',
            'text': """REPRESENTAÇÃO. PROPAGANDA ELEITORAL IRREGULAR. RIO DE JANEIRO/RJ.
            A propaganda eleitoral em bens públicos é vedada pela legislação eleitoral.
            No caso dos autos, restou comprovada a fixação irregular de material de campanha
            em poste de iluminação pública no município do Rio de Janeiro. Aplicação de multa
            e determinação de remoção do material. Representação julgada procedente.""",
            'metadata': {
                'number': '78.234',
                'year': 2023,
                'type': 'Acórdão',
                'tema': 'Propaganda Eleitoral',
                'city': 'Rio de Janeiro'
            }
        },
        {
            'title': 'Acórdão TRE-RJ 89.456 - Abuso de Poder Niterói',
            'text': """AÇÃO DE INVESTIGAÇÃO JUDICIAL ELEITORAL. ABUSO DE PODER POLÍTICO.
            NITERÓI/RJ. Configurado o abuso de poder político mediante utilização de
            estrutura da administração pública em favor de candidatura. A jurisprudência
            do TRE-RJ é firme no sentido de coibir tais práticas que desequilibram o pleito.
            AIJE julgada procedente. Cassação do registro.""",
            'metadata': {
                'number': '89.456',
                'year': 2022,
                'type': 'Acórdão',
                'tema': 'Abuso de Poder',
                'city': 'Niterói'
            }
        },
    ],
    "TRE-PR": [
        {
            'title': 'Acórdão TRE-PR 12.567 - Eleições Curitiba',
            'text': """RECURSO ORDINÁRIO. IMPUGNAÇÃO DE CANDIDATURA. CURITIBA/PR.
            A condição de elegibilidade deve ser aferida no momento do registro da candidatura.
            Tratando-se de candidato com domicílio eleitoral regularmente comprovado no
            estado do Paraná, não há óbice ao deferimento do registro. A jurisprudência
            do TRE-PR tem sido reiterada neste sentido. Recurso provido.""",
            'metadata': {
                'number': '12.567',
                'year': 2023,
                'type': 'Acórdão',
                'tema': 'Registro de Candidatura',
                'city': 'Curitiba'
            }
        },
        {
            'title': 'Acórdão TRE-PR 23.890 - Propaganda Londrina',
            'text': """REPRESENTAÇÃO. PROPAGANDA ANTECIPADA. LONDRINA/PR.
            Caracteriza propaganda eleitoral antecipada a divulgação de conteúdo com pedido
            explícito de voto antes do período permitido pela legislação. No caso analisado,
            verificou-se que houve divulgação em redes sociais antes do prazo legal em
            Londrina. Aplicação de multa. Representação procedente.""",
            'metadata': {
                'number': '23.890',
                'year': 2023,
                'type': 'Acórdão',
                'tema': 'Propaganda Eleitoral',
                'city': 'Londrina'
            }
        },
    ],
    "TRE-SC": [
        {
            'title': 'Acórdão TRE-SC 34.678 - Registro Florianópolis',
            'text': """REGISTRO DE CANDIDATURA. ELEIÇÕES MUNICIPAIS. FLORIANÓPOLIS/SC.
            O candidato deve apresentar certidão de quitação eleitoral, que engloba a
            regularidade do cadastro, a inexistência de multas eleitorais inadimplidas e
            a apresentação de contas de campanha. Verificado o cumprimento de todos os
            requisitos pelo candidato no estado de Santa Catarina. Registro deferido.""",
            'metadata': {
                'number': '34.678',
                'year': 2023,
                'type': 'Acórdão',
                'tema': 'Registro de Candidatura',
                'city': 'Florianópolis'
            }
        },
        {
            'title': 'Acórdão TRE-SC 45.901 - Inelegibilidade Joinville',
            'text': """RECURSO. INELEGIBILIDADE. REJEIÇÃO DE CONTAS. JOINVILLE/SC.
            A rejeição de contas de gestão pública por irregularidade insanável e por decisão
            irrecorrível do órgão competente gera inelegibilidade por 8 anos, nos termos
            da Lei Complementar 64/90. Comprovada a rejeição de contas do recorrente quando
            prefeito de município de Santa Catarina. Recurso não provido.""",
            'metadata': {
                'number': '45.901',
                'year': 2022,
                'type': 'Acórdão',
                'tema': 'Inelegibilidade',
                'city': 'Joinville'
            }
        },
    ]
}
