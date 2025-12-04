import { TerrariumScene } from './core/TerrariumScene';
import { UIController } from './ui/UIController';
import { StatusMonitor } from './systems/StatusMonitor';

class TerrariumApp {
  private scene: TerrariumScene;
  private ui: UIController;

  constructor() {
    // Initialize Three.js scene
    this.scene = new TerrariumScene(document.getElementById('canvas-container')!);

    // Initialize UI
    this.ui = new UIController(this.scene);

    // Initialize status monitoring
    new StatusMonitor(this.scene, this.ui);

    // Hide loading screen
    setTimeout(() => {
      const loading = document.getElementById('loading');
      if (loading) {
        loading.style.opacity = '0';
        setTimeout(() => loading.remove(), 500);
      }
    }, 1500);

    // Start animation loop
    this.animate();
  }

  private animate = () => {
    requestAnimationFrame(this.animate);
    this.scene.update();
    this.scene.render();
  }
}

// Start the app
new TerrariumApp();
