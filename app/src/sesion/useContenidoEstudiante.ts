import { api, type LeccionEstudiante, type UnidadEstudiante } from '@/api/cliente';
import { useConsulta } from '@/sesion/useConsulta';

// Perfil, unidades (estrellas, etiqueta, sugerida) y lecciones del estudiante, compartidos por
// las tres pestañas. React Query guarda cada consulta una vez, así que cambiar de pestaña o
// abrir un detalle no vuelve a pedirlas.
export function useContenidoEstudiante() {
  const perfil = useConsulta('perfil-estudiante', api.perfilEstudiante);
  const unidades = useConsulta('unidades', api.unidades);
  const lecciones = useConsulta('lecciones', api.lecciones);
  const consultas = [perfil, unidades, lecciones];

  const reintentar = () => consultas.forEach((c) => c.isError && c.refetch());
  const error = consultas.find((c) => c.isError)?.error;

  if (!perfil.data || !unidades.data || !lecciones.data) {
    return { listo: false as const, error, reintentar };
  }
  const curso = perfil.data.curso;
  const porUnidad = new Map<string, UnidadEstudiante>(unidades.data.map((u) => [u.id, u]));
  return {
    listo: true as const,
    reintentar,
    estudiante: perfil.data,
    unidades: unidades.data,
    porUnidad,
    delCurso: lecciones.data.filter((l) => l.curso === curso),
    anteriores: lecciones.data.filter((l) => l.curso < curso),
    leccion: (unidadId: string) => lecciones.data.find((l) => l.unidadId === unidadId),
  };
}

// "Lección 3", o "Lección 3 · 4° básico" si es de un curso anterior al del estudiante.
export function nombreLeccion(l: LeccionEstudiante, cursoEstudiante: number) {
  return l.curso === cursoEstudiante
    ? `Lección ${l.numero}`
    : `Lección ${l.numero} · ${l.curso}° básico`;
}
