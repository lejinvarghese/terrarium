import * as THREE from 'three';
import { gsap } from 'gsap';

export class BotEntity {
  public group: THREE.Group;
  public name: string;
  private sphere: THREE.Mesh;
  private glow: THREE.Mesh;
  private orbitRing: THREE.Mesh;
  private label: THREE.Sprite;
  private active: boolean = true;
  private time: number = 0;

  constructor(name: string, _emoji: string, color: number) {
    this.name = name;
    this.group = new THREE.Group();

    // Create main sphere - more sophisticated material
    const geometry = new THREE.SphereGeometry(0.5, 64, 64);
    const material = new THREE.MeshPhysicalMaterial({
      color: color,
      metalness: 0.9,
      roughness: 0.1,
      emissive: color,
      emissiveIntensity: 1.2,  // Brighter for bloom
      clearcoat: 1.0,
      clearcoatRoughness: 0.1,
      envMapIntensity: 1.5
    });

    this.sphere = new THREE.Mesh(geometry, material);
    this.sphere.castShadow = true;
    this.group.add(this.sphere);

    // Create softer glow effect
    const glowGeometry = new THREE.SphereGeometry(0.8, 32, 32);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.15,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide
    });

    this.glow = new THREE.Mesh(glowGeometry, glowMaterial);
    this.group.add(this.glow);

    // Create orbit ring - thinner, more elegant
    const ringGeometry = new THREE.RingGeometry(0.85, 0.87, 64);
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: color,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.25,
      blending: THREE.AdditiveBlending
    });

    this.orbitRing = new THREE.Mesh(ringGeometry, ringMaterial);
    this.orbitRing.rotation.x = Math.PI / 2;
    this.group.add(this.orbitRing);

    // Create label
    this.label = this.createLabel();
    this.group.add(this.label);

    // Add point light - stronger for bloom
    const light = new THREE.PointLight(color, 2, 8);
    light.castShadow = false; // Performance
    this.group.add(light);

    // Entrance animation
    this.animateEntrance();
  }

  private createLabel(): THREE.Sprite {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d')!;
    canvas.width = 256;
    canvas.height = 64;

    // Glassmorphic background
    const gradient = context.createLinearGradient(0, 0, 256, 64);
    gradient.addColorStop(0, 'rgba(20, 20, 40, 0.4)');
    gradient.addColorStop(1, 'rgba(30, 30, 60, 0.3)');
    context.fillStyle = gradient;
    context.fillRect(0, 0, canvas.width, canvas.height);

    // Subtle border glow
    context.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    context.lineWidth = 1;
    context.strokeRect(1, 1, canvas.width - 2, canvas.height - 2);

    // Modern sans-serif font - no emoji
    context.font = '600 32px "Inter", system-ui, sans-serif';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillStyle = '#ffffff';
    context.shadowColor = 'rgba(0, 0, 0, 0.5)';
    context.shadowBlur = 4;
    context.fillText(this.name, 128, 32);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      opacity: 0.9
    });
    const sprite = new THREE.Sprite(material);
    sprite.position.y = 1.5;
    sprite.scale.set(1.6, 0.4, 1);

    return sprite;
  }

  private animateEntrance() {
    this.group.scale.set(0, 0, 0);
    gsap.to(this.group.scale, {
      x: 1,
      y: 1,
      z: 1,
      duration: 1,
      ease: 'elastic.out(1, 0.5)'
    });
  }

  public setPosition(x: number, y: number, z: number) {
    this.group.position.set(x, y, z);
  }

  public setActive(active: boolean) {
    this.active = active;

    const targetEmissive = active ? 0.5 : 0.1;
    const targetOpacity = active ? 0.3 : 0.1;

    gsap.to((this.sphere.material as THREE.MeshStandardMaterial), {
      emissiveIntensity: targetEmissive,
      duration: 0.5
    });

    gsap.to((this.glow.material as THREE.MeshBasicMaterial), {
      opacity: targetOpacity,
      duration: 0.5
    });

    if (active) {
      // Pulse animation
      gsap.to(this.sphere.scale, {
        x: 1.2,
        y: 1.2,
        z: 1.2,
        duration: 0.3,
        yoyo: true,
        repeat: 1
      });
    }
  }

  public setVisible(visible: boolean) {
    this.group.visible = visible;
  }

  public update() {
    this.time += 0.02;

    // Float animation
    this.group.position.y += Math.sin(this.time) * 0.002;

    // Rotate glow
    this.glow.rotation.y += 0.01;

    // Rotate orbit ring
    this.orbitRing.rotation.z += 0.02;

    // Pulse glow when active
    if (this.active) {
      const scale = 1 + Math.sin(this.time * 2) * 0.1;
      this.glow.scale.set(scale, scale, scale);
    }

    // Make label face camera
    this.label.rotation.copy(this.group.rotation);
  }
}
