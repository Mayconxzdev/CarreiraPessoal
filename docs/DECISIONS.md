# Decisões de engenharia e produto

## 1. IA é reforço, não requisito

Descoberta, validação, deduplicação, matching determinístico, histórico e acompanhamento continuam operacionais sem provider de IA. Isso reduz lock-in e permite operação privada/local.

## 2. Career Goal Gate separado do matching

Aderência técnica não implica valor de carreira. O produto separa elegibilidade, aderência, legitimidade/confiança, valor da oportunidade e direção profissional.

## 3. Fonte de verdade profissional versionada

Currículo importado é prioritário; GitHub e portfólio acrescentam evidências públicas. Uma mudança relevante cria nova versão e invalida artefatos que dependiam do snapshot antigo.

## 4. Evidência antes de texto persuasivo

Resume Router e componentes de IA recebem fatos/projetos sustentados; métricas, senioridade, liderança e produção recebem tratamento mais restritivo para reduzir afirmações inventadas.

## 5. Human-in-the-loop no efeito externo

O Companion pode preparar campos e anexos, mas não executa o envio final. A decisão reduz risco de candidatura errada e mantém o usuário responsável pela ação externa.

## 6. Suporte de ATS sem marketing inflado

O registry reconhece 102 famílias/plataformas, mas o código atual possui 11 coletores diretos dedicados. Famílias sem API pública universal ficam como capture/detect em vez de serem anunciadas como integração completa.

## 7. Local-first e sidecar

A UI Tauri conversa com uma API FastAPI local em loopback. Dados ficam em SQLite no perfil local do usuário; extras como modelos, container runtime, SearXNG ou Qdrant são capacidades opcionais.

## 8. Installer-first

O usuário final não deveria instalar Python, Node ou Rust. O pipeline produz sidecar PyInstaller + Tauri/NSIS e só promove o candidato depois de install/reinstall/uninstall smoke no Windows.
