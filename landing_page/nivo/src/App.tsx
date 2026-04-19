import { Routes, Route } from 'react-router-dom';
import { Navbar } from '@/components/layout/navbar';
import { HomePage } from '@/pages/home';
import { NotFoundPage } from '@/pages/not-found';
import { SectionPage, type SectionPageProps } from '@/pages/section-page';

const appPage: SectionPageProps = {
  badge: 'App',
  title: 'Una cuenta simple para pagar y moverte global',
  description:
    'Nivo arranca con lo que más se usa: enviar, recibir, pagar con tarjeta virtual y entender cada movimiento sin letra pequeña.',
  proof: 'Pagos en COP, tarjeta, links de cobro y recibos claros',
  stats: [
    { value: 'COP', label: 'día a día' },
    { value: 'Tarjeta', label: 'virtual' },
    { value: 'Recibos', label: 'verificables' },
  ],
  cards: [
    {
      title: 'Pagos por celular',
      description:
        'Envía y recibe plata con una experiencia familiar para Colombia, pensada para onboarding rápido y soporte local.',
    },
    {
      title: 'Tarjeta virtual',
      description:
        'Compra online, separa gastos y apaga la tarjeta cuando algo no te cuadre, usando un emisor aliado.',
    },
    {
      title: 'Movimientos claros',
      description:
        'Cada pago queda con estado, costo, contraparte y comprobante para que puedas reclamar o compartirlo.',
    },
  ],
  calloutTitle: 'Activa Nivo desde lo cotidiano',
  calloutDescription:
    'La adopción empieza con pagos simples. Las monedas, crypto y acciones se suman cuando el usuario ya confía en la cuenta.',
};

const currencyPage: SectionPageProps = {
  badge: 'Monedas',
  title: 'COP, USD y EUR sin perderte entre bancos y apps',
  description:
    'Cambia dinero entre monedas con tasa visible, fee claro y ejecución a través de aliados habilitados para divisas.',
  proof: 'Hecho para freelancers, viajeros y colombianos en el exterior',
  stats: [
    { value: 'COP', label: 'Colombia' },
    { value: 'USD', label: 'cobros globales' },
    { value: 'EUR', label: 'Europa' },
  ],
  cards: [
    {
      title: 'Precio antes de confirmar',
      description:
        'Ves cuánto entregas, cuánto recibes, cuál es el fee y cuánto tiempo se bloquea la tasa.',
    },
    {
      title: 'Bolsillos por moneda',
      description:
        'Organiza saldos y movimientos por moneda para separar gastos locales, viajes y cobros internacionales.',
    },
    {
      title: 'Alertas de cambio',
      description:
        'Marca una tasa objetivo y recibe alerta cuando el mercado llegue al nivel que esperas.',
    },
  ],
  calloutTitle: 'El puente natural entre Colombia y el mundo',
  calloutDescription:
    'Nivo puede servir primero a quienes ya sienten el dolor: freelancers, nómadas y familias que viven entre monedas.',
};

const investingPage: SectionPageProps = {
  badge: 'Invertir',
  title: 'Crypto y acciones como módulos separados, claros y responsables',
  description:
    'Nivo prepara módulos de crypto, acciones y ETFs con partners responsables de ejecución y custodia, sin promesas de rendimiento y con riesgos visibles antes de operar.',
  proof: 'Riesgos, costos y límites visibles antes de cada orden',
  stats: [
    { value: 'Crypto', label: 'partner VASP' },
    { value: 'Stocks', label: 'broker aliado' },
    { value: 'ETFs', label: 'acceso global' },
  ],
  cards: [
    {
      title: 'Crypto con límites',
      description:
        'Configura montos máximos, compras recurrentes y confirmaciones para evitar decisiones impulsivas.',
    },
    {
      title: 'Acciones y ETFs',
      description:
        'Acceso a instrumentos globales mediante broker autorizado, con separación clara entre cuenta e inversión.',
    },
    {
      title: 'Sin letra pequeña',
      description:
        'Antes de comprar ves riesgo, fee, partner, tipo de orden y estado de ejecución.',
    },
  ],
  calloutTitle: 'Inversión sin disfrazarla de billetera',
  calloutDescription:
    'El producto debe sentirse simple, pero legalmente ordenado: cada módulo tiene su responsable y sus disclosures.',
};

const securityPage: SectionPageProps = {
  badge: 'Seguridad',
  title: 'Seguridad post-cuántica explicada en lenguaje normal',
  description:
    'Validación de identidad, antifraude, recibos verificables y criptografía post-cuántica aplicada donde protege datos de larga vida.',
  proof: 'ML-KEM para llaves, ML-DSA para firmas y modo híbrido durante la transición',
  stats: [
    { value: 'ML-KEM', label: 'llaves' },
    { value: 'ML-DSA', label: 'firmas' },
    { value: 'Híbrido', label: 'transición' },
  ],
  cards: [
    {
      title: 'PQC donde sí aporta',
      description:
        'El intercambio de llaves protege secretos compartidos y las firmas verificables sellan órdenes, recibos y estados relevantes.',
    },
    {
      title: 'Antifraude operativo',
      description:
        'La protección post-cuántica se combina con identidad, señales de dispositivo, límites, revisión de patrones y confirmaciones adicionales.',
    },
    {
      title: 'Criptoagilidad',
      description:
        'Los algoritmos y llaves se versionan para migrar si los estándares evolucionan, sin rehacer la experiencia ni el core financiero.',
    },
  ],
  calloutTitle: 'Seguridad que se siente como control, no como jerga',
  calloutDescription:
    'El usuario no necesita aprender criptografía. Necesita saber que su identidad, sus comprobantes y sus decisiones quedan protegidos con controles actuales y preparación para amenazas futuras.',
};

const businessPage: SectionPageProps = {
  badge: 'Empresas',
  title: 'Infraestructura financiera para pymes digitales y fintechs',
  description:
    'Nivo puede vender recibos verificables, onboarding, antifraude y APIs de pago mientras el producto B2C gana tracción.',
  proof: 'Revenue B2B temprano sin custodiar fondos propios',
  stats: [
    { value: 'API', label: 'recibos' },
    { value: 'KYC', label: 'onboarding' },
    { value: 'Risk', label: 'antifraude' },
  ],
  cards: [
    {
      title: 'Pymes exportadoras',
      description:
        'Cobros internacionales, comprobantes y conciliación para equipos pequeños que venden fuera de Colombia.',
    },
    {
      title: 'Fintechs medianas',
      description:
        'Integración de recibos firmados, monitoreo de riesgo y seguridad avanzada sin montar un equipo criptográfico.',
    },
    {
      title: 'Compliance desde el inicio',
      description:
        'KYC, monitoreo LAFT y trazabilidad como parte del producto, no como un parche cuando llegue escala.',
    },
  ],
  calloutTitle: 'B2B ayuda a financiar el sueño B2C',
  calloutDescription:
    'La API puede generar caja y validación técnica mientras la app crece con usuarios reales.',
};

const developersPage: SectionPageProps = {
  badge: 'API PQC',
  title: 'Infraestructura post-cuántica para fintechs, banca y equipos de riesgo',
  description:
    'Nivo abre una capa API para recibos verificables, identidad, antifraude y firmas preparadas para amenazas futuras, sin obligarte a montar un equipo criptográfico desde cero.',
  proof: 'Recibos firmados · KYC trazable · controles de riesgo · evolución criptográfica',
  stats: [
    { value: 'PQC', label: 'firmas y llaves' },
    { value: 'API', label: 'integración' },
    { value: 'Audit', label: 'trazabilidad' },
  ],
  cards: [
    {
      title: 'Recibos verificables',
      description:
        'Sella órdenes, comprobantes y eventos críticos con firmas verificables listas para conciliación, soporte y auditoría.',
    },
    {
      title: 'Onboarding y KYC',
      description:
        'Integra validación de identidad, revisión operativa y trazabilidad de acceso sin separar la experiencia del compliance.',
    },
    {
      title: 'Capa de transición',
      description:
        'Empieza con compatibilidad actual y suma criptografía post-cuántica donde más importa: datos de larga vida y pruebas duraderas.',
    },
  ],
  calloutTitle: 'Explora la API PQC con el equipo de Nivo',
  calloutDescription:
    'Pensada para aliados que necesitan seguridad futura sin convertir su producto en un laboratorio criptográfico.',
};

const App = () => {
  return (
    <main className="min-h-screen bg-nivo-paper">
      <Navbar />

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/app" element={<SectionPage {...appPage} />} />
        <Route path="/plataforma" element={<SectionPage {...appPage} />} />
        <Route path="/platform" element={<SectionPage {...appPage} />} />
        <Route path="/monedas" element={<SectionPage {...currencyPage} />} />
        <Route path="/invertir" element={<SectionPage {...investingPage} />} />
        <Route path="/seguridad" element={<SectionPage {...securityPage} />} />
        <Route path="/trustlayer" element={<SectionPage {...securityPage} />} />
        <Route path="/trust-layer" element={<SectionPage {...securityPage} />} />
        <Route path="/empresas" element={<SectionPage {...businessPage} />} />
        <Route path="/developers" element={<SectionPage {...developersPage} />} />
        <Route path="/architecture" element={<SectionPage {...businessPage} />} />
        <Route path="/arquitectura" element={<SectionPage {...businessPage} />} />
        <Route path="/por-que" element={<HomePage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </main>
  );
};

export default App;
