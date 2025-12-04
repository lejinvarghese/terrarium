import * as THREE from 'three';

export class ParticleSystem {
  private scene: THREE.Scene;
  private particles: THREE.Points[] = [];
  private time: number = 0;

  constructor(scene: THREE.Scene) {
    this.scene = scene;
    this.createParticleSystems();
  }

  private createParticleSystems() {
    // Create floating data particles
    this.createFloatingParticles();

    // Create connection lines between entities
    this.createDataStreams();
  }

  private createFloatingParticles() {
    const particleCount = 500;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      // Random position in terrarium bounds
      positions[i * 3] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 1] = Math.random() * 10;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 20;

      // Random colors (cyan, green, pink)
      const colorChoice = Math.random();
      if (colorChoice < 0.33) {
        colors[i * 3] = 0;
        colors[i * 3 + 1] = 1;
        colors[i * 3 + 2] = 0.5;
      } else if (colorChoice < 0.66) {
        colors[i * 3] = 0;
        colors[i * 3 + 1] = 0.8;
        colors[i * 3 + 2] = 1;
      } else {
        colors[i * 3] = 1;
        colors[i * 3 + 1] = 0.4;
        colors[i * 3 + 2] = 0.6;
      }

      sizes[i] = Math.random() * 0.1 + 0.05;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    const material = new THREE.PointsMaterial({
      size: 0.1,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const particles = new THREE.Points(geometry, material);
    this.particles.push(particles);
    this.scene.add(particles);
  }

  private createDataStreams() {
    // Create spiraling particle streams
    for (let stream = 0; stream < 5; stream++) {
      const particleCount = 100;
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(particleCount * 3);

      const angle = (stream / 5) * Math.PI * 2;
      const radius = 8;

      for (let i = 0; i < particleCount; i++) {
        const t = i / particleCount;
        const spiralAngle = angle + t * Math.PI * 4;
        const spiralRadius = radius * (1 - t * 0.5);
        const height = t * 8;

        positions[i * 3] = Math.cos(spiralAngle) * spiralRadius;
        positions[i * 3 + 1] = height;
        positions[i * 3 + 2] = Math.sin(spiralAngle) * spiralRadius;
      }

      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

      const color = stream % 2 === 0 ? 0x00ff88 : 0x00d4ff;
      const material = new THREE.PointsMaterial({
        color: color,
        size: 0.08,
        transparent: true,
        opacity: 0.4,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      });

      const particles = new THREE.Points(geometry, material);
      this.particles.push(particles);
      this.scene.add(particles);
    }
  }

  public update() {
    this.time += 0.01;

    this.particles.forEach((particleSystem, index) => {
      if (index === 0) {
        // Animate floating particles
        const positions = particleSystem.geometry.attributes.position.array as Float32Array;
        for (let i = 0; i < positions.length; i += 3) {
          positions[i + 1] += Math.sin(this.time + i) * 0.01;

          // Reset particles that float too high
          if (positions[i + 1] > 10) {
            positions[i + 1] = 0;
          }
        }
        particleSystem.geometry.attributes.position.needsUpdate = true;
      } else {
        // Rotate data streams
        particleSystem.rotation.y += 0.005;
      }
    });
  }

  public setVisible(visible: boolean) {
    this.particles.forEach(p => p.visible = visible);
  }
}
