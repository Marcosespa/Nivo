export interface MediaAbout {
  overview: string;
  conclusion: string;
}

export interface MediaContentItem {
  src: string;
  poster?: string;
  background: string;
  title: string;
  date: string;
  scrollToExpand: string;
  about: MediaAbout;
}

export type MediaType = 'video' | 'image';

export type MediaContentCollection = Record<MediaType, MediaContentItem>;

export const mediaContent: MediaContentCollection = {
  video: {
    src: '/assets/blackmarble_2016_rotate_720p.mp4',
    poster:
      'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=2200&q=80',
    background:
      'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=2200&q=80',
    title: 'Tu plata, blindada para el futuro',
    date: 'Nivo',
    scrollToExpand: 'Descubre cómo te protege',
    about: {
      overview:
        'Nivo es la primera billetera digital colombiana con seguridad post-cuántica. Paga, cambia monedas e invierte desde una cuenta simple — con el mismo blindaje que la banca suiza apenas empieza a adoptar.',
      conclusion:
        'Tu identidad, tus recibos y tu plata quedan protegidos hoy contra los ataques de los próximos 20 años. Porque lo que robar mañana ya lo guardan hoy.',
    },
  },
  image: {
    src: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=2200&q=80',
    background:
      'https://images.pexels.com/photos/30596210/pexels-photo-30596210.jpeg?cs=srgb&dl=pexels-zelch-30596210.jpg&fm=jpg',
    title: 'Tu plata, blindada para el futuro',
    date: 'Nivo',
    scrollToExpand: 'Descubre cómo te protege',
    about: {
      overview:
        'Nivo es la primera billetera digital colombiana con seguridad post-cuántica. Paga, cambia monedas e invierte desde una cuenta simple — con el mismo blindaje que la banca suiza apenas empieza a adoptar.',
      conclusion:
        'Tu identidad, tus recibos y tu plata quedan protegidos hoy contra los ataques de los próximos 20 años. Porque lo que robar mañana ya lo guardan hoy.',
    },
  },
};
