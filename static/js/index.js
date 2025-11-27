// ===== CORTE DIGITAL - MAIN INDEX =====
// This file loads all modules in the correct order

console.log('🚀 Carregando Corte Digital...');

// Load order is important:
// 1. API configuration
// 2. Utilities
// 3. Theme
// 4. Navigation
// 5. Auth
// 6. Shared components (notifications, micro-interactions)
// 7. Page-specific modules (loaded in HTML)

// Mark as loaded
window.corteDigitalLoaded = true;
console.log('✅ Corte Digital carregado');
