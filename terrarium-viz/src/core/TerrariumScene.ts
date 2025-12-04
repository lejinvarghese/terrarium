import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { BotEntity } from '../entities/BotEntity';
import { ServiceEntity } from '../entities/ServiceEntity';
import { ParticleSystem } from '../systems/ParticleSystem';
import { TerraDome } from '../entities/TerraDome';

export class TerrariumScene {
  public scene: THREE.Scene;
  public camera: THREE.PerspectiveCamera;
  public renderer: THREE.WebGLRenderer;
  public controls: OrbitControls;
  public composer: EffectComposer;
  public bloomPass: UnrealBloomPass;

  public bots: BotEntity[] = [];
  public services: ServiceEntity[] = [];
  public particleSystem: ParticleSystem;
  public dome: TerraDome;

  constructor(container: HTMLElement) {

    // Scene setup
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x050510); // Deeper, richer black
    this.scene.fog = new THREE.FogExp2(0x050510, 0.02); // Exponential fog for depth

    // Camera setup
    this.camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    this.camera.position.set(0, 8, 15);

    // Renderer setup
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 0.8; // Darker, moodier
    container.appendChild(this.renderer.domElement);

    // Post-processing setup
    this.composer = new EffectComposer(this.renderer);
    const renderPass = new RenderPass(this.scene, this.camera);
    this.composer.addPass(renderPass);

    // Bloom pass for glowing effects
    this.bloomPass = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight),
      0.8,   // strength - subtle but present
      0.6,   // radius - wider glow
      0.3    // threshold - only bright objects glow
    );
    this.composer.addPass(this.bloomPass);

    // Controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.minDistance = 5;
    this.controls.maxDistance = 30;
    this.controls.maxPolarAngle = Math.PI / 2 + 0.3;

    // Lighting
    this.setupLighting();

    // Create dome
    this.dome = new TerraDome();
    this.scene.add(this.dome.group);

    // Create bots
    this.createBots();

    // Create services
    this.createServices();

    // Particle system
    this.particleSystem = new ParticleSystem(this.scene);

    // Window resize handler
    window.addEventListener('resize', this.onWindowResize);
  }

  private setupLighting() {
    // Subtle ambient light - very dark
    const ambientLight = new THREE.AmbientLight(0x1a1a2e, 0.15);
    this.scene.add(ambientLight);

    // Main directional light - cooler, more cinematic
    const sunLight = new THREE.DirectionalLight(0x7799ff, 0.4);
    sunLight.position.set(15, 25, 10);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.near = 0.5;
    sunLight.shadow.camera.far = 50;
    this.scene.add(sunLight);

    // Rim light for depth
    const rimLight = new THREE.DirectionalLight(0x4a5cff, 0.3);
    rimLight.position.set(-10, 5, -10);
    this.scene.add(rimLight);

    // Subtle accent lights - lower intensity
    const accentLight1 = new THREE.PointLight(0x00e5a0, 0.8, 15);
    accentLight1.position.set(-10, 3, 8);
    this.scene.add(accentLight1);

    const accentLight2 = new THREE.PointLight(0x6b4ce8, 0.8, 15);
    accentLight2.position.set(10, 3, -8);
    this.scene.add(accentLight2);
  }

  private createBots() {
    // Sophisticated, muted color palette - deep, rich tones
    const botConfigs = [
      { name: 'Cassia', emoji: '🌅', color: 0xff7b00, position: 0 },  // Deep amber
      { name: 'Sage', emoji: '🧙', color: 0x6b4ce8, position: 1 },    // Royal purple
      { name: 'Freya', emoji: '💪', color: 0x00e5a0, position: 2 },   // Teal green
      { name: 'Nigella', emoji: '🍝', color: 0xd45d3a, position: 3 }, // Burnt sienna
      { name: 'Nyx', emoji: '🚀', color: 0x00b8ff, position: 4 },     // Electric blue
      { name: 'Anya', emoji: '🎨', color: 0xe05780, position: 5 },    // Rose
      { name: 'Casper', emoji: '🤖', color: 0x3ba4cc, position: 6 },  // Deep cyan
      { name: 'Pepper', emoji: '⚡', color: 0xdc3b84, position: 7 },  // Magenta
      { name: 'Luci', emoji: '🔮', color: 0x7c3aed, position: 8 },    // Violet
    ];

    const radius = 6;
    const angleStep = (Math.PI * 2) / botConfigs.length;

    botConfigs.forEach((config, index) => {
      const angle = angleStep * index;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const y = Math.sin(angle * 2) * 0.5; // Slight vertical variation

      const bot = new BotEntity(config.name, config.emoji, config.color);
      bot.setPosition(x, y + 2, z);
      this.bots.push(bot);
      this.scene.add(bot.group);
    });
  }

  private createServices() {
    const serviceConfigs = [
      { name: 'Dome', icon: '🌐', color: 0x4a90e2, position: { x: -10, z: -10 } },
      { name: 'Engine', icon: '⚙️', color: 0xe74c3c, position: { x: 10, z: -10 } },
      { name: 'Portal', icon: '📱', color: 0x2ecc71, position: { x: -10, z: 10 } },
      { name: 'Bridge', icon: '🌉', color: 0xf39c12, position: { x: 10, z: 10 } },
      { name: 'Archive', icon: '📚', color: 0x9b59b6, position: { x: 0, z: 12 } },
    ];

    serviceConfigs.forEach(config => {
      const service = new ServiceEntity(config.name, config.icon, config.color);
      service.setPosition(config.position.x, -2, config.position.z);
      this.services.push(service);
      this.scene.add(service.group);
    });
  }

  public update() {
    this.controls.update();

    // Update all entities
    this.bots.forEach(bot => bot.update());
    this.services.forEach(service => service.update());
    this.particleSystem.update();
    this.dome.update();
  }

  public render() {
    this.composer.render();
  }

  private onWindowResize = () => {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.composer.setSize(window.innerWidth, window.innerHeight);
  }

  public resetCamera() {
    this.camera.position.set(0, 8, 15);
    this.controls.target.set(0, 0, 0);
    this.controls.update();
  }

  public toggleBots(visible: boolean) {
    this.bots.forEach(bot => bot.setVisible(visible));
  }

  public toggleServices(visible: boolean) {
    this.services.forEach(service => service.setVisible(visible));
  }

  public toggleParticles(visible: boolean) {
    this.particleSystem.setVisible(visible);
  }

  public updateBotStatus(botName: string, active: boolean) {
    const bot = this.bots.find(b => b.name === botName);
    if (bot) {
      bot.setActive(active);
    }
  }

  public updateServiceStatus(serviceName: string, active: boolean) {
    const service = this.services.find(s => s.name === serviceName);
    if (service) {
      service.setActive(active);
    }
  }
}
