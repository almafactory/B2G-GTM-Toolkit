import {
  AbsoluteFill,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {captions, deliverables, heroNumbers, promptText} from "./story";

const sec = (seconds: number) => seconds * 30;

export const DemoVideo = () => {
  return (
    <AbsoluteFill className="canvas">
      <Sequence from={sec(0)} durationInFrames={sec(20)}>
        <HookScene />
      </Sequence>
      <Sequence from={sec(20)} durationInFrames={sec(25)}>
        <PromptScene />
      </Sequence>
      <Sequence from={sec(45)} durationInFrames={sec(65)}>
        <PipelineScene />
      </Sequence>
      <Sequence from={sec(110)} durationInFrames={sec(40)}>
        <DeliverablesScene />
      </Sequence>
      <Sequence from={sec(150)} durationInFrames={sec(30)}>
        <CloseScene />
      </Sequence>
      <CaptionTrack />
    </AbsoluteFill>
  );
};

const Brand = () => (
  <div className="brand">
    <div className="brandMark">▥</div>
    <div>
      <span>GovBridge</span> <strong>GTM</strong>
    </div>
  </div>
);

const MediaSlot = ({label, detail}: {label: string; detail: string}) => (
  <div className="mediaSlot">
    <div className="slotLabel">{label}</div>
    <div className="slotDetail">{detail}</div>
  </div>
);

const HookScene = () => {
  const frame = useCurrentFrame();
  const entrance = spring({frame, fps: 30, config: {damping: 18}});
  return (
    <AbsoluteFill className="scene twoCol">
      <Brand />
      <div className="copyBlock" style={{opacity: entrance}}>
        <p className="eyebrow">Video demo hackaton</p>
        <h1>Andrea vende SaaS a alcaldias.</h1>
        <p>
          SECOP tiene los datos, pero ella pierde horas traduciendo compras
          publicas en acciones comerciales.
        </p>
        <div className="heroMetric">{heroNumbers.researchHours}</div>
      </div>
      <div className="messyDesk">
        <MediaSlot
          label="HeyGen: Andrea hook"
          detail="Avatar frente a SECOP, Excel, LinkedIn, PDFs y Notion vacio."
        />
        {["SECOP II", "Excel", "LinkedIn", "PDF pliego", "Notion vacio"].map(
          (tab, index) => (
            <div
              className="floatingTab"
              key={tab}
              style={{
                transform: `translate(${index * 38}px, ${index * 30}px) rotate(${
                  -4 + index * 2
                }deg)`,
              }}
            >
              {tab}
            </div>
          ),
        )}
      </div>
    </AbsoluteFill>
  );
};

const PromptScene = () => {
  const frame = useCurrentFrame();
  const graphOpacity = interpolate(frame, [18, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const nodes = ["ICP", "Target Accounts", "SECOP", "Notion", "Outreach"];
  return (
    <AbsoluteFill className="scene">
      <Brand />
      <div className="terminal">
        <div className="terminalTop">Claude Code</div>
        <div className="prompt">{promptText}</div>
      </div>
      <div className="graph" style={{opacity: graphOpacity}}>
        {nodes.map((node) => (
          <div className="graphNode" key={node}>
            {node}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const PipelineScene = () => {
  return (
    <AbsoluteFill className="scene split">
      <Brand />
      <div className="panel">
        <MediaSlot
          label="Grabacion real: Claude Code"
          detail="CLI corriendo el toolkit, acelerado 8x, sin secrets ni comandos largos."
        />
        <CodeLines />
      </div>
      <div className="panel notionPanel">
        <MediaSlot
          label="Grabacion real: Notion"
          detail="Bases B2G Target Accounts, SECOP Research, Opportunities y GTM Outputs llenandose."
        />
        <NotionRows />
      </div>
      <Counters />
    </AbsoluteFill>
  );
};

const CodeLines = () => {
  const lines = [
    "Construyendo ICP B2G...",
    "Priorizando entidades publicas...",
    "Cruzando procesos SECOP...",
    "Calculando fit score...",
    "Sincronizando GTM OS en Notion...",
    "Generando outreach y discovery prep...",
  ];
  return (
    <div className="codeLines">
      {lines.map((line, index) => (
        <div key={line} style={{opacity: 0.45 + index * 0.09}}>
          <span>$</span> {line}
        </div>
      ))}
    </div>
  );
};

const NotionRows = () => {
  const rows = [
    ["Alcaldia de Pereira", "88", "Expansion TIC"],
    ["Alcaldia de Manizales", "84", "Gestion documental"],
    ["Alcaldia de Medellin", "82", "Recaudo municipal"],
    ["Gobernacion del Quindio", "72", "Modernizacion"],
  ];
  return (
    <div className="notionTable">
      {rows.map((row) => (
        <div className="notionRow" key={row[0]}>
          <span>{row[0]}</span>
          <strong>{row[1]}</strong>
          <em>{row[2]}</em>
        </div>
      ))}
    </div>
  );
};

const Counters = () => {
  const frame = useCurrentFrame();
  const count = (to: number) =>
    Math.round(
      interpolate(frame, [0, 1500], [0, to], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      }),
    );
  return (
    <div className="counters">
      <Counter label="Entidades analizadas" value={count(heroNumbers.entities)} />
      <Counter
        label="Procesos SECOP cruzados"
        value={count(heroNumbers.secopProcesses)}
      />
      <Counter
        label="Oportunidades con evidencia"
        value={count(heroNumbers.opportunities)}
      />
      <Counter label="Pipeline detectado" value={heroNumbers.pipeline} />
    </div>
  );
};

const Counter = ({label, value}: {label: string; value: string | number}) => (
  <div className="counter">
    <strong>{value}</strong>
    <span>{label}</span>
  </div>
);

const DeliverablesScene = () => (
  <AbsoluteFill className="scene deliverablesScene">
    <Brand />
    <div className="sectionHeader">
      <p className="eyebrow">El entregable que usa el AE</p>
      <h2>Alcaldia de Medellin - Modernizacion TIC</h2>
    </div>
    <div className="deliverableGrid">
      {deliverables.map((item) => (
        <div className="deliverable" key={item.title}>
          <h3>{item.title}</h3>
          <p>{item.body}</p>
        </div>
      ))}
    </div>
    <div className="evidenceBar">
      Evidencia SECOP: proceso, modalidad, monto historico y enlace original.
    </div>
  </AbsoluteFill>
);

const CloseScene = () => {
  const frame = useCurrentFrame();
  const items = [
    "De 6 horas de research manual a 8 minutos.",
    "De listas frias a 9 oportunidades con evidencia SECOP.",
    "De CRM vacio a GTM OS vivo en Notion.",
  ];
  return (
    <AbsoluteFill className="scene closeScene">
      <Brand />
      <div className="closeLines">
        {items.map((item, index) => (
          <div
            className="closeLine"
            key={item}
            style={{
              opacity: interpolate(frame, [index * 42, index * 42 + 18], [0, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
            }}
          >
            {item}
          </div>
        ))}
      </div>
      <div className="tagline">
        B2G GTM Toolkit - de datos publicos a pipeline comercial.
      </div>
    </AbsoluteFill>
  );
};

const CaptionTrack = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame / fps;
  const active = captions.find((caption) => time >= caption.start && time < caption.end);

  if (!active) {
    return null;
  }

  return <div className="caption">{active.text}</div>;
};
