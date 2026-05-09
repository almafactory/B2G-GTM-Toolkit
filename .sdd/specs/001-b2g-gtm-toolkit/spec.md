# Especificación de la funcionalidad: B2G-GTM-Toolkit

**ID de la funcionalidad**: `001-b2g-gtm-toolkit`
**Creado**: 2026-05-09
**Estado**: Draft

## Escenarios de usuario y pruebas

### Historia de usuario 1 - Definir un ICP B2G a partir de contexto real de cliente (Prioridad: P1)

Un contratista B2G o miembro de un equipo GTM proporciona el contexto base del negocio, clientes actuales, competidores, detalles de la oferta, mejores clientes, clientes de mal ajuste e hipótesis de mercado. El toolkit guía al agente con las preguntas correctas, usa las skills GTM existentes como metodología base y produce un Ideal Customer Profile práctico para compradores del sector público colombiano.

**Por qué esta prioridad**: El ICP es la base de todo el flujo posterior. Si el sistema no identifica qué entidades públicas vale la pena perseguir, la investigación en SECOP, la prospección, las propuestas y la preparación de reuniones producirán salidas genéricas o de bajo valor.

**Prueba independiente**: Proporcionar un perfil de contratista de ejemplo con 5-10 clientes y verificar que el toolkit produzca un ICP con tipos de entidad objetivo, criterios de ajuste, descalificadores, disparadores de compra, roles objetivo y nivel de confianza.

**Escenarios de aceptación**:

1. **Dado** un usuario con contexto parcial pero utilizable de clientes y oferta, **cuando** inicia el flujo de ICP, **entonces** el toolkit solicita las entradas base faltantes antes de producir el ICP.
2. **Dado** un usuario con clientes previos como alcaldías o gobernaciones, **cuando** se completa el flujo de ICP, **entonces** la salida identifica segmentos de entidad pública objetivo y explica por qué encajan bien.
3. **Dado** evidencia de cliente débil o insuficiente, **cuando** el toolkit produce el ICP, **entonces** lo etiqueta como hipótesis y lista la evidencia que aún falta para validarlo.

---

### Historia de usuario 2 - Construir una lista de cuentas objetivo a partir del ICP (Prioridad: P1)

Un usuario GTM toma la salida del ICP y le pide al toolkit que identifique entidades públicas y cuentas que coincidan con el perfil objetivo. El toolkit convierte los criterios del ICP en una lista estructurada de cuentas objetivo que puede guiar la investigación en SECOP y la priorización comercial.

**Por qué esta prioridad**: Los usuarios necesitan una lista accionable antes de poder investigar contratos, historial de compra, oportunidades próximas y mensajes específicos por cuenta.

**Prueba independiente**: Usar un ICP completado y verificar que el toolkit devuelva una lista priorizada de cuentas con justificación de ajuste, tipo de cuenta, región/categoría cuando esté disponible y siguiente acción de investigación.

**Escenarios de aceptación**:

1. **Dado** un ICP completado, **cuando** el usuario inicia la prospección, **entonces** el toolkit produce cuentas agrupadas o rankeadas por ajuste.
2. **Dado** un candidato a cuenta objetivo, **cuando** la cuenta no tiene suficiente evidencia para coincidir con el ICP, **entonces** el toolkit la marca como incierta en lugar de tratarla como calificada.
3. **Dado** criterios de cuenta objetivo que involucren tipo de entidad pública, geografía, categoría o patrón de compra, **cuando** se crea la lista, **entonces** cada cuenta incluye la razón por la que pertenece a la lista.

---

### Historia de usuario 3 - Investigar oportunidades SECOP e historial de compra (Prioridad: P1)

Un contratista quiere encontrar licitaciones, contratos y oportunidades en SECOP que sean relevantes para su ICP y su oferta. El toolkit ayuda a ejecutar investigaciones repetibles sobre datos de SECOP, captura contratos históricos y oportunidades actuales, y transforma los hallazgos en inteligencia estructurada de cuentas y oportunidades.

**Por qué esta prioridad**: El valor central del producto es reducir la investigación manual de SECOP y ayudar a los contratistas a identificar oportunidades del sector público más relevantes cada mes.

**Prueba independiente**: Proporcionar una cuenta objetivo o criterios de búsqueda del ICP y verificar que el toolkit produzca salidas de investigación estructuradas para contratos, oportunidades, compradores, proveedores, fechas, valores, justificación de relevancia y siguiente acción recomendada.

**Escenarios de aceptación**:

1. **Dada** una lista de cuentas objetivo, **cuando** corre la investigación SECOP, **entonces** el toolkit registra contratos históricos relevantes y oportunidades activas o recientes para cada cuenta donde existan datos.
2. **Dada** una oportunidad encontrada en SECOP, **cuando** el toolkit la evalúa, **entonces** resume por qué es relevante o no relevante para la oferta del usuario.
3. **Dadas** necesidades repetidas de investigación, **cuando** un usuario proporciona las mismas entradas a lo largo del tiempo, **entonces** el toolkit soporta recolección repetible sin requerir que el agente navegue y copie manualmente datos de SECOP.

---

### Historia de usuario 4 - Guardar inteligencia GTM en Notion (Prioridad: P1)

Un equipo quiere un sistema operativo GTM persistente donde ICPs, cuentas, hallazgos SECOP, oportunidades, señales de compra, planes de outreach, briefs de reuniones, propuestas y responsables se almacenen en bases de datos estructuradas de Notion.

**Por qué esta prioridad**: La salida debe poder reutilizarse por equipos de ventas, emprendedores y account executives. Sin almacenamiento estructurado, el toolkit solo crea documentos aislados y no puede soportar flujos recurrentes.

**Prueba independiente**: Ejecutar el flujo para un ICP y tres cuentas, y luego verificar que los registros resultantes puedan encontrarse en las bases de datos de Notion esperadas con los datos de cuenta, oportunidad e investigación vinculados.

**Escenarios de aceptación**:

1. **Dado** un workspace sin la estructura requerida de Notion, **cuando** el usuario inicia un flujo que necesita almacenamiento, **entonces** el toolkit verifica si existen las bases de datos requeridas antes de guardar la investigación.
2. **Dado** datos SECOP investigados, **cuando** se almacenan, **entonces** quedan vinculados al ICP relevante, a la cuenta objetivo, a la oportunidad y a la persona responsable cuando se conoce.
3. **Dado** registros duplicados o ya investigados, **cuando** el toolkit guarda nuevos hallazgos, **entonces** evita crear duplicados confusos y conserva el último estado conocido.

---

### Historia de usuario 5 - Generar entregables para account executives (Prioridad: P2)

Un account executive usa la inteligencia guardada de cuentas y oportunidades para crear campañas de outreach, briefs de preparación de reuniones, briefs de propuesta y business cases para oportunidades del sector público.

**Por qué esta prioridad**: Después de capturar la investigación, el siguiente valor proviene de convertir esa inteligencia en activos de ejecución comercial que ahorran tiempo y mejoran la calidad.

**Prueba independiente**: Seleccionar una oportunidad investigada y verificar que el toolkit cree una secuencia de outreach, un brief de preparación de reunión y un brief de propuesta/business case usando la investigación almacenada como material de origen.

**Escenarios de aceptación**:

1. **Dada** una cuenta con historial de compra en SECOP, **cuando** el usuario pide outreach, **entonces** el toolkit crea una campaña ligada a las necesidades de la cuenta, el comportamiento histórico de compra y los posibles disparadores de compra.
2. **Dada** una reunión próxima, **cuando** el usuario pide preparación, **entonces** el toolkit produce un brief conciso con contexto de cuenta, contexto de oportunidad, preguntas clave, posibles objeciones y el ask recomendado.
3. **Dada** una oportunidad de licitación relevante, **cuando** el usuario pide apoyo para propuesta, **entonces** el toolkit produce un brief que ayude a evaluar ajuste, requisitos, posicionamiento y siguientes pasos.

---

### Historia de usuario 6 - Monitorear señales de compra y notificar a los responsables (Prioridad: P2)

Un equipo GTM quiere enriquecimiento continuo de leads, detección de señales de compra y notificaciones al responsable cuando aparezca una oportunidad o señal de cuenta relevante.

**Por qué esta prioridad**: Las oportunidades B2G son sensibles al tiempo. El toolkit debería ayudar a los equipos a actuar sobre señales en lugar de depender solo de investigación manual periódica.

**Prueba independiente**: Configurar una cuenta objetivo de ejemplo y un responsable, simular o detectar una nueva señal relevante y verificar que el sistema registre la señal y notifique al responsable con la acción recomendada.

**Escenarios de aceptación**:

1. **Dadas** cuentas objetivo con responsables, **cuando** aparecen nuevas oportunidades SECOP o señales de compra relevantes, **entonces** el toolkit crea un registro de señal e identifica al responsable.
2. **Dada** una señal con baja relevancia, **cuando** se evalúa, **entonces** el toolkit la marca con menor prioridad o suprime la notificación innecesaria.
3. **Dado** un enriquecimiento recurrente, **cuando** el toolkit actualiza datos de cuenta, **entonces** preserva la investigación previa y resalta lo que cambió.

---

### Casos límite

- El usuario no tiene clientes existentes y solo puede proporcionar cuentas ideales o suposiciones.
- Los mejores clientes del usuario no se mapean de forma limpia a categorías de entidades del sector público.
- Los datos de SECOP están incompletos, duplicados, desactualizados o son inconsistentes entre registros.
- Varias oportunidades parecen relevantes pero tienen cronogramas, requisitos o señales de presupuesto conflictivos.
- Un workspace de Notion no tiene las bases de datos requeridas o tiene un esquema similar pero incompatible.
- La misma entidad pública aparece con nombres o escrituras diferentes.
- Un responsable de lead falta, está inactivo o tiene demasiadas cuentas.
- Una licitación es comercialmente relevante pero imposible de perseguir por tiempo, elegibilidad, documentación o restricciones de calificación.

## Requisitos

### Requisitos funcionales

- **FR-001**: El sistema DEBE guiar a los usuarios a través de las entradas GTM base necesarias para definir un ICP, incluyendo oferta, clientes actuales, mejores clientes, peores clientes, competidores, supuestos del mercado objetivo y etapa de la empresa.
- **FR-002**: El sistema DEBE usar la metodología representada por las skills de ventas en `E:\skills\ventas` como base para la definición de ICP, prospección, investigación de cuentas, calificación, outreach, preparación de reuniones y outbound basado en señales.
- **FR-003**: El sistema DEBE producir un brief de ICP que incluya criterios de ajuste firmográfico/de entidad pública, criterios situacionales, disparadores de compra, roles del comité de compra, descalificadores, señales observables y nivel de confianza.
- **FR-004**: El sistema DEBE convertir el ICP en una lista de cuentas objetivo de entidades del sector público o segmentos de cuenta relevantes para ventas B2G en Colombia.
- **FR-005**: El sistema DEBE soportar flujos de investigación que recojan historial de compra de SECOP, contratos, proveedores, detalles de oportunidad, fechas, valores y justificación de relevancia para cuentas y oportunidades objetivo.
- **FR-006**: El sistema DEBE distinguir entre oportunidades activas, contratos históricos, inteligencia a nivel de cuenta y señales de compra.
- **FR-007**: El sistema DEBE estructurar las salidas de investigación para que puedan reutilizarlas los account executives en outreach, reuniones, propuestas y business cases.
- **FR-008**: El sistema DEBE verificar que existan las bases de datos y relaciones requeridas de Notion antes de guardar inteligencia GTM estructurada.
- **FR-009**: El sistema DEBE almacenar o actualizar ICPs, cuentas, oportunidades, registros de investigación SECOP, señales, assets de outreach, briefs de reuniones, briefs de propuesta y responsables en Notion.
- **FR-010**: El sistema DEBE detectar y manejar cuentas duplicadas, oportunidades duplicadas o hallazgos SECOP repetidos de forma que mantenga el workspace comprensible.
- **FR-011**: El sistema DEBE generar salidas de campañas de outreach a partir de la inteligencia almacenada de cuenta, oportunidad y señal.
- **FR-012**: El sistema DEBE generar briefs de preparación de reuniones a partir de la inteligencia almacenada de cuenta y oportunidad.
- **FR-013**: El sistema DEBE generar briefs de propuesta o business case para oportunidades SECOP seleccionadas.
- **FR-014**: El sistema DEBE soportar enriquecimiento recurrente de datos de leads y cuentas.
- **FR-015**: El sistema DEBE soportar detección recurrente de señales de compra y notificar al responsable cuando se encuentre una señal relevante.
- **FR-016**: El sistema DEBE etiquetar salidas inciertas, incompletas o de baja confianza en lugar de presentarlas como hechos validados.
- **FR-017**: El sistema DEBE preservar referencias de fuente o provenance para hallazgos derivados de SECOP para que los usuarios puedan rastrear por qué se recomendó una oportunidad o cuenta.
- **FR-018**: El sistema DEBE permitir que el usuario revise y apruebe salidas clave antes de que se usen en flujos posteriores.
- **FR-019**: El sistema DEBE soportar flujos y salidas en español para B2G, con soporte en inglés donde sea útil para comandos de la herramienta o configuración técnica.
- **FR-020**: El sistema DEBE proporcionar una configuración estilo toolkit que pueda instalarse o reutilizarse localmente por agentes de codificación de IA como Codex o Claude Code.
- **FR-021**: El sistema DEBE proporcionar un esquema por defecto del workspace GTM de Notion que pueda verificarse, crearse o iterarse más adelante sin bloquear la primera implementación.
- **FR-022**: El sistema DEBE soportar Slack y email como canales de notificación planificados para los responsables.
- **FR-023**: El sistema DEBE acotar la primera entrega a datos de SECOP colombiano dejando espacio para sumar otras fuentes de contratación pública más adelante.

### Entidades clave

- **Business Profile**: La empresa contratista o B2G que usa el toolkit, incluyendo qué vende, clientes actuales, competidores, fortalezas, restricciones e hipótesis de mercado.
- **ICP**: El perfil ideal de cliente del sector público derivado del contexto de clientes e investigación, incluyendo tipos de entidad objetivo, reglas de ajuste, descalificadores, disparadores de compra y nivel de confianza.
- **Target Account**: Una entidad pública o segmento de cuenta que coincide con el ICP y debe ser investigada o perseguida.
- **SECOP Research Record**: Un hallazgo estructurado de SECOP, incluyendo información de contrato u oportunidad, referencia de fuente, justificación de relevancia y relación con una cuenta.
- **Opportunity**: Una licitación, proceso de compra, oportunidad de contrato o evento comercial accionable específico que pueda justificar outreach o trabajo de propuesta.
- **Buying Signal**: Un cambio o evento relevante que indique que una cuenta objetivo puede valer la pena contactar o monitorear.
- **Responsible Owner**: La persona responsable de actuar sobre una cuenta, oportunidad o señal.
- **Outreach Campaign**: Un conjunto planificado de mensajes o acciones basado en inteligencia de cuenta y señales de compra.
- **Meeting Prep Brief**: Un artefacto breve de preparación para una reunión de cuenta u oportunidad.
- **Proposal / Business Case Brief**: Un artefacto estructurado que ayuda a evaluar, posicionar y preparar una oportunidad del sector público.
- **Notion GTM Workspace**: El sistema de bases de datos enlazadas donde se almacenan, relacionan y actualizan las salidas del toolkit.

## Criterios de éxito

### Resultados medibles

- **SC-001**: Un usuario puede completar el flujo base de ICP y recibir un brief de ICP sin decidir manualmente qué preguntas GTM hacer.
- **SC-002**: El toolkit puede transformar un ICP en una lista priorizada de cuentas con una justificación clara de ajuste.
- **SC-003**: Para una cuenta objetivo u oportunidad seleccionada, el toolkit puede producir registros estructurados de investigación SECOP reutilizables en flujos posteriores.
- **SC-004**: Las bases de datos requeridas de Notion pueden verificarse o prepararse antes de almacenar las salidas de investigación.
- **SC-005**: Una oportunidad guardada puede usarse para generar al menos tres salidas para account executives: outreach, preparación de reunión y brief de propuesta/business case.
- **SC-006**: El enriquecimiento recurrente puede identificar una señal nueva o cambiada y enrutarla a un responsable.
- **SC-007**: Los usuarios pueden procesar más oportunidades B2G relevantes por mes que con investigación SECOP y preparación documental totalmente manual.
- **SC-008**: Los usuarios pueden rastrear cada cuenta, oportunidad o señal recomendada hasta su evidencia subyacente o su justificación de origen.
