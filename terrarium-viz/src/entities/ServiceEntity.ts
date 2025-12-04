import * as THREE from 'three';
import { gsap } from 'gsap';

export class ServiceEntity {
  public group: THREE.Group;
  public name: string;
  private pillar: THREE.Mesh;
  private top: THREE.Mesh;
  private icon: THREE.Sprite;
  private iconText: string;
  private active: boolean = false;
  private time: number = 0;
  private energyRings: THREE.Mesh[] = [];

  constructor(name: string, iconText: string, color: number) {
    this.name = name;
    this.iconText = iconText;
    this.group = new THREE.Group();

    // Create pillar
    const pillarGeometry = new THREE.CylinderGeometry(0.4, 0.5, 4, 8);
    const pillarMaterial = new THREE.MeshStandardMaterial({
      color: 0x2a2f4a,
      metalness: 0.8,
      roughness: 0.3,
      emissive: color,
      emissiveIntensity: 0.1
    });

    this.pillar = new THREE.Mesh(pillarGeometry, pillarMaterial);
    this.pillar.position.y = 2;
    this.pillar.castShadow = true;
    this.group.add(this.pillar);

    // Create top platform
    const topGeometry = new THREE.CylinderGeometry(0.6, 0.4, 0.3, 8);
    const topMaterial = new THREE.MeshStandardMaterial({
      color: color,
      metalness: 0.9,
      roughness: 0.1,
      emissive: color,
      emissiveIntensity: 0.3
    });

    this.top = new THREE.Mesh(topGeometry, topMaterial);
    this.top.position.y = 4.15;
    this.group.add(this.top);

    // Create icon
    this.icon = this.createIcon();
    this.icon.position.y = 4.5;
    this.group.add(this.icon);

    // Create energy rings
    for (let i = 0; i < 3; i++) {
      const ringGeometry = new THREE.TorusGeometry(0.5 + i * 0.2, 0.02, 16, 32);
      const ringMaterial = new THREE.MeshBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.3,
        blending: THREE.AdditiveBlending
      });

      const ring = new THREE.Mesh(ringGeometry, ringMaterial);
      ring.rotation.x = Math.PI / 2;
      ring.position.y = 1 + i * 0.8;
      this.energyRings.push(ring);
      this.group.add(ring);
    }

    // Add point light
    const light = new THREE.PointLight(color, 0.5, 8);
    light.position.y = 4;
    this.group.add(light);

    // Entrance animation
    this.animateEntrance();
  }

  private createIcon(): THREE.Sprite {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d')!;
    canvas.width = 128;
    canvas.height = 128;

    context.fillStyle = 'rgba(0, 0, 0, 0.8)';
    context.fillRect(0, 0, canvas.width, canvas.height);

    context.font = '64px Arial';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(this.iconText, 64, 64);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(1, 1, 1);

    return sprite;
  }

  private animateEntrance() {
    this.group.position.y = -5;
    this.group.scale.set(1, 0, 1);

    gsap.to(this.group.position, {
      y: 0,
      duration: 1.5,
      ease: 'power2.out',
      delay: Math.random() * 0.5
    });

    gsap.to(this.group.scale, {
      y: 1,
      duration: 1.5,
      ease: 'elastic.out(1, 0.3)',
      delay: Math.random() * 0.5
    });
  }

  public setPosition(x: number, y: number, z: number) {
    this.group.position.set(x, y, z);
  }

  public setActive(active: boolean) {
    this.active = active;

    const targetEmissive = active ? 0.5 : 0.1;
    const targetOpacity = active ? 0.5 : 0.2;

    gsap.to((this.pillar.material as THREE.MeshStandardMaterial), {
      emissiveIntensity: targetEmissive,
      duration: 0.5
    });

    this.energyRings.forEach(ring => {
      gsap.to(ring.material, {
        opacity: targetOpacity,
        duration: 0.5
      });
    });

    if (active) {
      // Pulse animation
      gsap.to(this.top.scale, {
        x: 1.2,
        y: 1.2,
        z: 1.2,
        duration: 0.4,
        yoyo: true,
        repeat: 1
      });
    }
  }

  public setVisible(visible: boolean) {
    this.group.visible = visible;
  }

  public update() {
    this.time += 0.01;

    // Rotate icon
    this.icon.rotation.z = Math.sin(this.time) * 0.1;

    // Animate energy rings
    this.energyRings.forEach((ring, i) => {
      ring.position.y = 1 + i * 0.8 + Math.sin(this.time * 2 + i) * 0.1;
      ring.rotation.z += 0.01 * (i % 2 === 0 ? 1 : -1);
    });

    // Pulse top when active
    if (this.active) {
      const scale = 1 + Math.sin(this.time * 3) * 0.05;
      this.top.scale.set(scale, 1, scale);
    }
  }
}
