const map = L.map("map").setView([10.3910, -75.4794], 13);

const lightTiles = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors"
});
const darkTiles = L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
  attribution: "© CartoDB Dark Matter",
});
lightTiles.addTo(map);

const coloresPorSupervisor = {
  "JHOSELIN ARGEL": "#e74c3c",
  "RAUL MEZA": "#3498db",
  "DARWIN PASTRANA": "#2ecc71",
  "SERGIO MORENO": "#9b59b6",
  "JESUS OROZCO": "#f1c40f",
  "JUAN FERRER SUAREZ": "#1abc9c",
  "DAYANA TERAN": "#e67e22",
  "LUIS ANGULO": "#34495e",
};

const coloresAsignados = {};

function stringToHue(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash % 360);
}

function getColorPorSupervisor(nombre) {
  if (coloresPorSupervisor[nombre]) return coloresPorSupervisor[nombre];
  if (coloresAsignados[nombre]) return coloresAsignados[nombre];

  const hue = stringToHue(nombre);
  const color = `hsl(${hue}, 70%, 50%)`;
  coloresAsignados[nombre] = color;
  return color;
}

function getColorByEtapa(etapa, isDarkMode = false) {
  if (isDarkMode) {
    switch (etapa) {
      case "Niño": return "#5dade2";
      case "Adolescente": return "#f7dc6f";
      case "Adulto": return "#58d68d";
      default: return "#bbb";
    }
  } else {
    switch (etapa) {
      case "Niño": return "#3498db";
      case "Adolescente": return "#f39c12";
      case "Adulto": return "#2ecc71";
      default: return "gray";
    }
  }
}

function llenarOpcionesSupervisores() {
  const supervisores = new Set();
  marcadores.forEach((m) => {
    if (m.SUPERVISOR) {
      supervisores.add(m.SUPERVISOR);
    }
  });

  const filtroSupervisor = document.getElementById("filtroSupervisor");
  supervisores.forEach((sup) => {
    const option = document.createElement("option");
    option.value = sup;
    option.textContent = sup;
    filtroSupervisor.appendChild(option);
  });
}

let vistaActual = "supervisor";
let chartInstance = null;
const marcadoresPorCedula = {};

function pintarMarcadores(vista) {
  map.eachLayer((layer) => {
    if (layer instanceof L.CircleMarker) map.removeLayer(layer);
  });

  const isDark = document.body.classList.contains("dark-mode");
  const filtroGenero = document.getElementById("filtroGenero").value;
  const filtroEstrato = document.getElementById("filtroEstrato").value;
  const filtroNivel = document.getElementById("filtroNivel").value;
  const filtroVotoCongreso = document.getElementById("filtroVotoCongreso").value.toUpperCase().trim();
  const filtroSupervisor = document.getElementById("filtroSupervisor").value;

  marcadores.forEach((item) => {
    if (item.lat && item.lon) {
      const votoCongreso = (item["VOTA POR CONGRESO"] || "").toUpperCase().trim();
      if (
        (filtroGenero && item.GENERO !== filtroGenero) ||
        (filtroEstrato && item.ESTRATO !== filtroEstrato) ||
        (filtroNivel && item["NIVEL EDUCATIVO"] !== filtroNivel) ||
        (filtroVotoCongreso && votoCongreso !== filtroVotoCongreso) ||
        (filtroSupervisor && item.SUPERVISOR !== filtroSupervisor)
      ) return;

      const color = vista === "etapa"
        ? getColorByEtapa(item.ETAPA, isDark)
        : getColorPorSupervisor(item.SUPERVISOR || "Otro");

      const marker = L.circleMarker([item.lat, item.lon], {
        radius: 8,
        color,
        fillColor: color,
        fillOpacity: 0.8,
      })
        .addTo(map)
        .bindPopup(`
          <strong>${item["NOMBRE COMPLETO"] || "Sin nombre"}</strong><br>
          Edad: ${item.EDAD || "Desconocida"}<br>
          Género: ${item.GENERO || "N/D"}<br>
          Estrato: ${item.ESTRATO || "N/A"}<br>
          Nivel educativo: ${item["NIVEL EDUCATIVO"] || "N/A"}<br>
          Vota Congreso: ${item["VOTA POR CONGRESO"] || "N/A"}<br>
          Supervisor: ${item.SUPERVISOR || "N/A"}<br>
          Etapa: ${item.ETAPA || "Desconocida"}
        `);

      if (item.CEDULA) {
        marcadoresPorCedula[item.CEDULA] = marker;
      }
    }
  });
}

function buscarPorCedula() {
  const cedula = document.getElementById("inputCedula").value.trim();
  const marker = marcadoresPorCedula[cedula];

  if (marker) {
    map.setView(marker.getLatLng(), 17);
    marker.openPopup();
  } else {
    alert("No se encontró un registro con esa cédula.");
  }
}

// Comentamos la función de la gráfica
/*
function crearGrafico(labels, values, darkMode = false) {
  ...
}
*/

document.getElementById("toggleDarkMode").addEventListener("click", () => {
  const isDark = document.body.classList.toggle("dark-mode");
  document.getElementById("toggleDarkMode").textContent = isDark ? "☀️ Modo Claro" : "🌙 Modo Oscuro";
  map.removeLayer(isDark ? lightTiles : darkTiles);
  (isDark ? darkTiles : lightTiles).addTo(map);
  pintarMarcadores(vistaActual);
  // crearGrafico(supervisorLabels, supervisorValues, isDark);
});

// Comentamos el botón de cambiar vista
/*
document.getElementById("toggleVista").addEventListener("click", () => {
  vistaActual = vistaActual === "supervisor" ? "etapa" : "supervisor";
  pintarMarcadores(vistaActual);
  document.getElementById("toggleVista").textContent =
    vistaActual === "supervisor" ? "Cambiar a vista por ETAPA" : "Cambiar a vista por SUPERVISOR";
});
*/

["filtroGenero", "filtroEstrato", "filtroNivel", "filtroVotoCongreso", "filtroSupervisor"].forEach(id => {
  document.getElementById(id).addEventListener("change", () => pintarMarcadores(vistaActual));
});

function llenarOpcionesNivelEducativo() {
  const niveles = new Set();
  marcadores.forEach((m) => {
    if (m["NIVEL EDUCATIVO"]) {
      niveles.add(m["NIVEL EDUCATIVO"]);
    }
  });

  const filtroNivel = document.getElementById("filtroNivel");
  niveles.forEach((nivel) => {
    const option = document.createElement("option");
    option.value = nivel;
    option.textContent = nivel;
    filtroNivel.appendChild(option);
  });
}

// Inicializar
llenarOpcionesNivelEducativo();
llenarOpcionesSupervisores();
pintarMarcadores(vistaActual);
// crearGrafico(supervisorLabels, supervisorValues);
