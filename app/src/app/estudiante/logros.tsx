import { PantallaProvisoria } from '@/components/PantallaProvisoria';

// Pestaña "Mis logros" (RF-E5, RF-G4): puntos, estrellas e insignias propias, sin comparación.
export default function Logros() {
  return (
    <PantallaProvisoria
      titulo="Mis logros"
      descripcion="Aquí irán tus puntos, estrellas e insignias. Solo te comparas contigo."
    />
  );
}
