import type { ReactNode } from 'react';

export interface FeatureTabContent {
  badge: string;
  title: string;
  description: string;
  buttonText: string;
  stats: string[];
  visualTitle: string;
  visualLines: string[];
}

export interface FeatureTab {
  value: string;
  icon: ReactNode;
  label: string;
  content: FeatureTabContent;
}

export interface FeatureSectionData {
  badge: string;
  heading: string;
  description: string;
  tabs: FeatureTab[];
}

const shieldIcon = (
  <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden="true">
    <path
      d="M12 2.5L20.5 6.5v7c0 4-2.8 7.5-8.5 9-5.7-1.5-8.5-5-8.5-9v-7L12 2.5Z"
      stroke="currentColor"
      strokeWidth="1.5"
    />
    <path d="m9 12.5 2 2 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

const atomIcon = (
  <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden="true">
    <ellipse cx="12" cy="12" rx="9" ry="4" stroke="currentColor" strokeWidth="1.5" />
    <ellipse cx="12" cy="12" rx="9" ry="4" stroke="currentColor" strokeWidth="1.5" transform="rotate(60 12 12)" />
    <ellipse cx="12" cy="12" rx="9" ry="4" stroke="currentColor" strokeWidth="1.5" transform="rotate(120 12 12)" />
    <circle cx="12" cy="12" r="2" fill="currentColor" />
  </svg>
);

const paymentIcon = (
  <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden="true">
    <rect x="2" y="5" width="20" height="14" rx="3" stroke="currentColor" strokeWidth="1.5" />
    <path d="M2 10h20" stroke="currentColor" strokeWidth="1.5" />
    <path d="M6 14h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

const fraudIcon = (
  <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden="true">
    <path
      d="M4 16c1.6-1.7 3.2-2.5 4.8-2.5 2.4 0 3.1 2.5 5.4 2.5 1.3 0 2.8-.8 4.8-3"
      stroke="currentColor"
      strokeWidth="1.5"
    />
    <circle cx="12" cy="8" r="3" stroke="currentColor" strokeWidth="1.5" />
    <path d="M4 8h2M18 8h2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

export const nivoFeatureTabs: FeatureSectionData = {
  badge: 'Todo en Nivo',
  heading: 'Una app simple para mover, cambiar e invertir tu plata',
  description:
    'Nivo combina la familiaridad de una billetera local con módulos globales para monedas, crypto y acciones. Cada operación separa precio, riesgo, partner responsable y recibo verificable.',
  tabs: [
    {
      value: 'cuenta',
      icon: paymentIcon,
      label: 'Cuenta diaria',
      content: {
        badge: 'Pagos · Tarjeta · QR',
        title: 'Tu cuenta para pagar, recibir y controlar el día a día.',
        description:
          'Envía plata por número de celular, recibe cobros con link, paga con tarjeta virtual y ve tus movimientos en tiempo real. El flujo se siente conocido para Colombia, pero con una capa de comprobantes más clara.',
        buttonText: 'Entrar a la beta',
        stats: [
          'P2P por celular y links de cobro',
          'Tarjeta virtual con emisor aliado',
          'Recibos listos para compartir o reclamar',
        ],
        visualTitle: 'nivo.wallet',
        visualLines: [
          'balance: COP $1,280,000',
          'card: activa',
          'pago_qr: aprobado',
          'recibo: verificado',
        ],
      },
    },
    {
      value: 'monedas',
      icon: atomIcon,
      label: 'Multi-moneda',
      content: {
        badge: 'COP · USD · EUR',
        title: 'Cambia monedas con precio transparente antes de aceptar.',
        description:
          'Guarda tu vida financiera en una sola vista: pesos para el día a día, dólares para ahorrar o cobrar afuera y euros para quienes viven entre LATAM y Europa. La ejecución ocurre con aliados habilitados para divisas.',
        buttonText: 'Ver monedas',
        stats: [
          'Tipo de cambio visible antes de confirmar',
          'Historial por moneda y categoría',
          'Alertas cuando el precio llega a tu meta',
        ],
        visualTitle: 'nivo.fx',
        visualLines: [
          'from: COP $850,000',
          'to: USD $205.44',
          'rate: bloqueada 60s',
          'fee: visible',
        ],
      },
    },
    {
      value: 'invertir',
      icon: fraudIcon,
      label: 'Crypto y acciones',
      content: {
        badge: 'Módulos por partner',
        title: 'Crypto, acciones y ETFs entran como módulos separados.',
        description:
          'Nivo no promete rendimientos ni esconde riesgos. Cada módulo de inversión se habilita con disclosures claros, límites configurables y un partner responsable de ejecución y custodia.',
        buttonText: 'Unirme a inversión',
        stats: [
          'Crypto con exchange o VASP aliado',
          'Acciones y ETFs con broker autorizado',
          'Riesgo y comisiones visibles antes de comprar',
        ],
        visualTitle: 'nivo.market',
        visualLines: [
          'asset: BTC',
          'order: compra recurrente',
          'limit: COP $120,000/semana',
          'risk: confirmado',
        ],
      },
    },
    {
      value: 'seguridad',
      icon: shieldIcon,
      label: 'Seguridad',
      content: {
        badge: 'Identidad · Antifraude · PQC',
        title: 'Protección para movimientos de hoy y datos de largo plazo.',
        description:
          'Nivo diseña la seguridad con controles cotidianos y criptografía post-cuántica estandarizada por NIST. ML-KEM protege el intercambio de llaves, ML-DSA firma órdenes y recibos, y el modo híbrido mantiene compatibilidad durante la transición.',
        buttonText: 'Ver seguridad',
        stats: [
          'Validación de identidad y señales de dispositivo',
          'PQC híbrido para datos que deben durar',
          'Firmas verificables para pagos, órdenes y recibos',
        ],
        visualTitle: 'nivo.guard',
        visualLines: [
          'identity: verificada',
          'key_exchange: ML-KEM + X25519',
          'receipt_signature: ML-DSA',
          'risk_signal: monitoreado',
        ],
      },
    },
  ],
};
