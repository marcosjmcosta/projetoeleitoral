"""
Agente Eleitoral Unificado 2026 — Servidor de Plugin OpenAI
Unifica @Agentes Eleitoral (MCP) + @Método Marcos (Agentes 22 e 23)
"""

import os
import secrets
import json
import httpx
from datetime import datetime
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ── Configurações ─────────────────────────────────────────────────────────────
AGENTES_ELEITORAL_BASE  = "https://gemini-mcp-eleitoral.onrender.com"
AGENTES_ELEITORAL_TOKEN = os.getenv("AGENTES_ELEITORAL_TOKEN", "")
AGENTES_ELEITORAL_ID    = os.getenv("AGENTES_ELEITORAL_CLIENT_ID", "gemini-eleitoral")

# Chave de acesso ao seu plugin (defina no Render como variável de ambiente)
PLUGIN_API_KEY = os.getenv("PLUGIN_API_KEY", "")

app = FastAPI(
    title="Agente Eleitoral Unificado 2026",
    description="Unifica @Agentes Eleitoral + @Método Marcos (Agentes 22 e 23)",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not PLUGIN_API_KEY or PLUGIN_API_KEY == "DEFINA_UMA_CHAVE_FORTE_AQUI":
        raise HTTPException(status_code=503, detail="Chave da API não configurada")
    if not credentials or not secrets.compare_digest(
        credentials.credentials.encode("utf-8"), PLUGIN_API_KEY.encode("utf-8")
    ):
        raise HTTPException(
            status_code=401,
            detail="Credencial ausente ou inválida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


# ── Helpers ───────────────────────────────────────────────────────────────────

async def fetch_agentes_eleitoral(path: str) -> dict:
    """Faz requisição autenticada ao servidor @Agentes Eleitoral."""
    url = f"{AGENTES_ELEITORAL_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {AGENTES_ELEITORAL_TOKEN}",
        "X-Client-ID": AGENTES_ELEITORAL_ID,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 200:
            try:
                return resp.json()
            except Exception:
                return {"conteudo": resp.text}
        else:
            raise HTTPException(status_code=resp.status_code, detail=f"Erro ao consultar @Agentes Eleitoral: {resp.text}")


# ── Endpoints Públicos (manifesto e logo) ──────────────────────────────────────

@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def plugin_manifest():
    """Retorna o manifesto do plugin OpenAI."""
    base_url = os.getenv("PLUGIN_BASE_URL", "https://SEU-SERVIDOR.onrender.com")
    manifest = {
        "schema_version": "v1",
        "name_for_human": "Agente Eleitoral Unificado 2026",
        "name_for_model": "agente_eleitoral_unificado",
        "description_for_human": "Assistente especializado em Direito e Operações Eleitorais. Integra manuais jurídicos (AIJE, AIME, propaganda, candidatura, contas) com agentes operacionais de votação e administração das eleições. Referências TSE e TRE-MT.",
        "description_for_model": (
            "Você é o Agente Eleitoral Unificado 2026, especializado em Direito Eleitoral e Operações Eleitorais.\n\n"
            "FONTE A - JURÍDICO: Use /materia/{id} para manuais e referências. IDs disponíveis em /materias.\n"
            "FONTE B - OPERACIONAL:\n"
            "- AGENTE 22 (Administração das Eleições): logística, zonas, seções, mesários, locais, prazos, administração pré/pós-eleição. Inicie com [AGENTE 22 ATIVADO].\n"
            "- AGENTE 23 (Votação, Apuração e Totalização): urnas, votação, apuração, BU, totalização, 2º turno, transmissão de dados. Inicie com [AGENTE 23 ATIVADO].\n"
            "REGRAS: Roteie para Fonte A (jurídico), Fonte B (operacional) ou ambas (híbrido). "
            "Cite sempre TSE/TRE-MT e o ID da matéria. Informe a data atual em prazos. "
            "Sinalize revisão humana quando necessário. Português do Brasil, linguagem técnico-jurídica."
        ),
        "auth": {
            "type": "service_http",
            "authorization_type": "bearer",
            "verification_tokens": {
                "openai": os.getenv("OPENAI_VERIFICATION_TOKEN", "")
            }
        },
        "api": {
            "type": "openapi",
            "url": f"{base_url}/openapi.json",
            "is_user_authenticated": False
        },
        "logo_url": f"{base_url}/logo.png",
        "contact_email": os.getenv("CONTACT_EMAIL", "contato@exemplo.com"),
        "legal_info_url": f"{base_url}/legal"
    }
    return JSONResponse(content=manifest)


@app.get("/legal", include_in_schema=False)
async def legal():
    return {"info": "Este plugin é de uso restrito para fins eleitorais legais."}


# ── Endpoints da API ───────────────────────────────────────────────────────────

@app.get(
    "/materias",
    summary="Lista todas as matérias disponíveis",
    description="Retorna a lista completa de IDs e títulos de matérias eleitorais disponíveis.",
    tags=["Agentes Eleitoral"],
    dependencies=[Depends(verify_token)],
)
async def listar_materias():
    """Lista todos os IDs de matérias eleitorais disponíveis."""
    materias = [
        # Advogados
        {"id": "advogado-aije-representacoes",         "titulo": "Advogado Eleitoralista - AIJE e Representações Especiais"},
        {"id": "advogado-aime",                         "titulo": "Advogado Eleitoralista - AIME"},
        {"id": "advogado-crimes-eleitorais",            "titulo": "Advogado Eleitoralista - Crimes Eleitorais"},
        {"id": "advogado-direito-resposta",             "titulo": "Advogado Eleitoralista - Direito de Resposta"},
        {"id": "advogado-infidelidade-partidaria",      "titulo": "Advogado Eleitoralista - Infidelidade Partidária e Justa Causa"},
        {"id": "advogado-orgaos-partidarios",           "titulo": "Advogado Eleitoralista - Órgãos Partidários e Intervenção"},
        {"id": "advogado-pesquisa-eleitoral",           "titulo": "Advogado Eleitoralista - Pesquisa Eleitoral"},
        {"id": "advogado-prestacao-contas-anual",       "titulo": "Advogado Eleitoralista - Prestação de Contas Anual"},
        {"id": "advogado-prestacao-contas-eleitorais",  "titulo": "Advogado Eleitoralista - Prestação de Contas de Campanha"},
        {"id": "advogado-propaganda-eleitoral",         "titulo": "Advogado Eleitoralista - Propaganda Eleitoral"},
        {"id": "advogado-rced",                         "titulo": "Advogado Eleitoralista - RCED"},
        {"id": "advogado-registro-candidatura-airc",    "titulo": "Advogado Eleitoralista - Registro de Candidatura e AIRC"},
        {"id": "advogado-suspensao-anotacao-partido",   "titulo": "Advogado Eleitoralista - Suspensão e Anotação de Partido"},
        # Operações 1º Grau
        {"id": "aije-embargos-declaracao",              "titulo": "Manual - AIJE (Embargos de Declaração)"},
        {"id": "aije-organizacao-saneamento",           "titulo": "Manual - AIJE (Organização e Saneamento)"},
        {"id": "aije-sentenca",                         "titulo": "Manual - AIJE (Sentença 1º Grau)"},
        {"id": "aije-tutela-urgencia",                  "titulo": "Manual - AIJE (Tutela de Urgência)"},
        {"id": "aime-embargos-declaracao",              "titulo": "Manual - AIME (Embargos de Declaração)"},
        {"id": "analise-prestacao-contas-anual",        "titulo": "Manual - Análise Técnica de PCA"},
        {"id": "analise-prestacao-contas-eleitorais",   "titulo": "Manual - Análise Técnica de PCE"},
        {"id": "analise-registro-candidatura",          "titulo": "Manual - Análise de Registro de Candidatura"},
        {"id": "cancelamento-inscricao-eleitoral",      "titulo": "Manual - Cancelamento de Inscrição Eleitoral"},
        {"id": "criacao-partido-sapf",                  "titulo": "Manual - Criação de Partido e Sistema SAPF"},
        {"id": "crimes-eleitorais-1grau",               "titulo": "Manual - Crimes Eleitorais (Sentença 1º Grau)"},
        {"id": "cumprimento-sentenca",                  "titulo": "Manual - Cumprimento de Sentença Eleitoral"},
        {"id": "direito-resposta",                      "titulo": "Manual - Direito de Resposta"},
        {"id": "duplicidade-filiacao",                  "titulo": "Manual - Duplicidade de Filiação Partidária"},
        {"id": "duplicidade-inscricoes-eleitorais",     "titulo": "Manual - Duplicidade de Inscrições Eleitorais"},
        {"id": "ementa-eleitoral",                      "titulo": "Manual - Ementa Eleitoral"},
        {"id": "habeas-corpus-je",                      "titulo": "Manual - Habeas Corpus na Justiça Eleitoral"},
        {"id": "pce-embargos-declaracao",               "titulo": "Manual - PCE (Embargos de Declaração)"},
        {"id": "pesquisa-eleitoral",                    "titulo": "Manual - Representação por Pesquisa Eleitoral Irregular"},
        {"id": "pesquisa-jurisprudenciaia",             "titulo": "Manual - Pesquisa de Jurisprudência (JurisprudênciaIA)"},
        {"id": "prestacao-contas-anual",                "titulo": "Manual - Prestação de Contas Anual (Partidária)"},
        {"id": "prestacao-contas-eleitorais",           "titulo": "Manual - Prestação de Contas Eleitorais (Campanha)"},
        {"id": "propaganda-eleitoral",                  "titulo": "Manual - Representação por Propaganda Eleitoral Irregular"},
        {"id": "propaganda-eleitoral-embargos",         "titulo": "Manual - Propaganda Eleitoral (Embargos)"},
        {"id": "propaganda-eleitoral-tutela-urgencia",  "titulo": "Manual - Propaganda Eleitoral (Tutela de Urgência)"},
        {"id": "registro-candidatura",                  "titulo": "Manual - Registro de Candidatura"},
        {"id": "regularizacao-eleitor-direitos-politicos", "titulo": "Manual - Regularização do Eleitor e Direitos Políticos"},
        {"id": "suspensao-orgao-partidario",            "titulo": "Manual - Suspensão de Órgão Partidário (SUSPOP)"},
        # Desembargador / 2º Grau
        {"id": "desembargador-aije-ementa-voto",        "titulo": "Manual - AIJE (Ementa + Voto de Desembargador)"},
        {"id": "desembargador-aime",                    "titulo": "Manual - AIME (Voto de Desembargador)"},
        {"id": "desembargador-crimes-eleitorais",       "titulo": "Manual - Crimes Eleitorais (Voto de Desembargador)"},
        {"id": "desembargador-cumprimento-sentenca",    "titulo": "Manual - Cumprimento de Sentença (Voto de Desembargador)"},
        {"id": "desembargador-direito-resposta",        "titulo": "Manual - Direito de Resposta (Voto de Desembargador)"},
        {"id": "desembargador-infidelidade-partidaria-justa-causa", "titulo": "Manual - Infidelidade Partidária e Justa Causa (Voto)"},
        {"id": "desembargador-ms-aije-representacoes",  "titulo": "MS - AIJE e Representações Especiais (2º Grau)"},
        {"id": "desembargador-ms-aime",                 "titulo": "MS - AIME (2º Grau)"},
        {"id": "desembargador-ms-crimes-eleitorais",    "titulo": "MS - Crimes Eleitorais (2º Grau)"},
        {"id": "desembargador-ms-cumprimento-sentenca", "titulo": "MS - Cumprimento de Sentença (2º Grau)"},
        {"id": "desembargador-ms-direito-resposta",     "titulo": "MS - Direito de Resposta (2º Grau)"},
        {"id": "desembargador-ms-infidelidade-partidaria", "titulo": "MS - Infidelidade Partidária (2º Grau)"},
        {"id": "desembargador-ms-orgaos-partidarios",   "titulo": "MS - Órgãos Partidários (2º Grau)"},
        {"id": "desembargador-ms-pesquisa-eleitoral",   "titulo": "MS - Pesquisa Eleitoral (2º Grau)"},
        {"id": "desembargador-ms-prestacao-contas-anual", "titulo": "MS - Prestação de Contas Anual (2º Grau)"},
        {"id": "desembargador-ms-prestacao-contas-eleitorais", "titulo": "MS - Prestação de Contas de Campanha (2º Grau)"},
        {"id": "desembargador-ms-propaganda-eleitoral", "titulo": "MS - Propaganda Eleitoral (2º Grau)"},
        {"id": "desembargador-ms-rced",                 "titulo": "MS - RCED (2º Grau)"},
        {"id": "desembargador-ms-suspensao-anotacao-partido", "titulo": "MS - Suspensão de Anotação de Partido (2º Grau)"},
        {"id": "desembargador-pca-ementa-voto",         "titulo": "Manual - PCA (Ementa + Voto de Desembargador)"},
        {"id": "desembargador-pce-ementa-voto",         "titulo": "Manual - PCE (Ementa + Voto de Desembargador)"},
        {"id": "desembargador-pesquisa-eleitoral",      "titulo": "Manual - Pesquisa Eleitoral (Voto de Desembargador)"},
        {"id": "desembargador-propaganda-eleitoral",    "titulo": "Manual - Propaganda Eleitoral (Voto de Desembargador)"},
        {"id": "desembargador-rcand-airc",              "titulo": "Manual - RCAND/AIRC (Voto de Desembargador)"},
        {"id": "desembargador-rced",                    "titulo": "Manual - RCED (Voto de Desembargador)"},
        {"id": "desembargador-registro-cancelamento-orgaos-partidarios", "titulo": "Manual - Registro e Cancelamento de Órgãos Partidários (Voto)"},
        {"id": "desembargador-suspensao-anotacao-partido", "titulo": "Manual - Suspensão e Anotação de Partido (Voto de Desembargador)"},
    ]
    return {"total": len(materias), "materias": materias}


@app.get(
    "/materia/{materia_id}",
    summary="Obtém manual e FIRAC de uma matéria eleitoral",
    description="Retorna o conteúdo completo (manual, FIRAC, referências) de uma matéria eleitoral pelo seu ID.",
    tags=["Agentes Eleitoral"],
    dependencies=[Depends(verify_token)],
)
async def get_materia(materia_id: str):
    """Consulta o manual e FIRAC de uma matéria no servidor @Agentes Eleitoral."""
    return await fetch_agentes_eleitoral(f"/api/materias/{materia_id}")


@app.get(
    "/materia/{materia_id}/referencias",
    summary="Obtém as referências legais de uma matéria",
    description="Retorna as referências (TSE, TRE, legislação) de uma matéria eleitoral.",
    tags=["Agentes Eleitoral"],
    dependencies=[Depends(verify_token)],
)
async def get_referencias(materia_id: str):
    """Consulta as referências legais de uma matéria no servidor @Agentes Eleitoral."""
    return await fetch_agentes_eleitoral(f"/api/materias/{materia_id}/referencias")


@app.get(
    "/agente22/contexto",
    summary="Contexto operacional do Agente 22 — Administração das Eleições",
    description="Retorna orientações e checklist do Agente 22 para procedimentos de administração eleitoral.",
    tags=["Método Marcos"],
    dependencies=[Depends(verify_token)],
)
async def agente22_contexto():
    """Retorna contexto e checklist do Agente 22 — Administração das Eleições."""
    return {
        "agente": "AGENTE 22 — ADMINISTRAÇÃO DAS ELEIÇÕES",
        "data_referencia": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "descricao": "Apoio operacional a cartórios e juízos eleitorais na administração das eleições.",
        "areas_de_atuacao": [
            "Logística e planejamento eleitoral",
            "Zonas e seções eleitorais",
            "Nomeação e treinamento de mesários",
            "Definição e vistoria de locais de votação",
            "Cronogramas e prazos eleitorais",
            "Procedimentos administrativos pré-eleição",
            "Procedimentos administrativos pós-eleição",
            "Gestão de materiais e urnas eletrônicas",
            "Procedimentos urgentes de administração",
        ],
        "referencias": ["TSE — Resolução nº 23.669/2021 e atualizações", "TRE-MT — Portarias e Instruções Normativas"],
        "aviso": "Decisões que envolvam inelegibilidade, cassação ou medidas judiciais requerem revisão humana por magistrado competente.",
    }


@app.get(
    "/agente23/contexto",
    summary="Contexto operacional do Agente 23 — Votação, Apuração e Totalização",
    description="Retorna orientações e checklist do Agente 23 para procedimentos de votação, apuração e totalização.",
    tags=["Método Marcos"],
    dependencies=[Depends(verify_token)],
)
async def agente23_contexto():
    """Retorna contexto e checklist do Agente 23 — Votação, Apuração e Totalização."""
    return {
        "agente": "AGENTE 23 — VOTAÇÃO, APURAÇÃO E TOTALIZAÇÃO",
        "data_referencia": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "descricao": "Apoio operacional a cartórios e juízos eleitorais nos procedimentos de votação, apuração e totalização.",
        "areas_de_atuacao": [
            "Abertura de urnas eletrônicas (zerésima)",
            "Procedimentos de votação presencial",
            "Seções especiais (hospitais, penitenciárias, exterior)",
            "Fechamento e encerramento de urnas",
            "Emissão do Boletim de Urna (BU)",
            "Apuração dos votos",
            "Totalização dos resultados",
            "Transmissão de dados ao TSE",
            "Contingências e incidentes durante a votação",
            "Procedimentos urgentes do 2º turno",
        ],
        "checklist_segundo_turno": [
            "Confirmar lista de seções e locais habilitados",
            "Verificar carga das urnas e lacres",
            "Conferir mesários nomeados e suplentes",
            "Verificar materiais (cabines, biometria, QR Code)",
            "Confirmar contato com TRE para contingências",
            "Checar procedimento de transmissão de dados pós-apuração",
        ],
        "referencias": ["TSE — Resolução nº 23.669/2021 e atualizações", "TRE-MT — Portarias e Instruções Normativas"],
        "aviso": "Incidentes graves durante a votação requerem comunicação imediata ao juiz eleitoral e ao TRE. Revisão humana obrigatória.",
    }


@app.get(
    "/status",
    summary="Status do servidor",
    tags=["Sistema"],
)
async def status():
    return {
        "status": "online",
        "plugin": "Agente Eleitoral Unificado 2026",
        "versao": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "fontes": {
            "agentes_eleitoral": AGENTES_ELEITORAL_BASE,
            "metodo_marcos": "Agentes 22 e 23 integrados",
        },
    }
