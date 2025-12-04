import * as THREE from 'three';

export class TerraDome {
  public group: THREE.Group;
  private dome: THREE.Mesh;
  private base: THREE.Mesh;
  private rings: THREE.Mesh[] = [];
  private time: number = 0;

  constructor() {
    this.group = new THREE.Group();

    // Create glass dome - more subtle, refined
    const domeGeometry = new THREE.SphereGeometry(10, 128, 64, 0, Math.PI * 2, 0, Math.PI / 2);
    const domeMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x4a5cff,
      transparent: true,
      opacity: 0.08,
      metalness: 0.0,
      roughness: 0.02,
      transmission: 0.95,
      thickness: 0.2,
      envMapIntensity: 0.5,
      clearcoat: 1,
      clearcoatRoughness: 0.05,
      side: THREE.DoubleSide,
      ior: 1.5
    });

    this.dome = new THREE.Mesh(domeGeometry, domeMaterial);
    this.dome.position.y = 0;
    this.group.add(this.dome);

    // Create base platform - darker, more refined
    const baseGeometry = new THREE.CylinderGeometry(11, 11, 0.5, 128);
    const baseMaterial = new THREE.MeshStandardMaterial({
      color: 0x0a0a15,
      metalness: 0.9,
      roughness: 0.1,
      emissive: 0x3a4cff,
      emissiveIntensity: 0.1
    });

    this.base = new THREE.Mesh(baseGeometry, baseMaterial);
    this.base.position.y = -0.25;
    this.base.receiveShadow = true;
    this.group.add(this.base);

    // Create energy rings
    this.createEnergyRings();

    // Add ground grid
    this.createGroundGrid();

    // Add ambient particles inside dome
    this.createAmbientParticles();
  }

  private createEnergyRings() {
    for (let i = 0; i < 3; i++) {
      const ringGeometry = new THREE.TorusGeometry(10 - i * 1.5, 0.03, 16, 100);
      const ringMaterial = new THREE.MeshBasicMaterial({
        color: i === 0 ? 0x6b4ce8 : i === 1 ? 0x00b8ff : 0xe05780,
        transparent: true,
        opacity: 0.2,
        blending: THREE.AdditiveBlending
      });

      const ring = new THREE.Mesh(ringGeometry, ringMaterial);
      ring.rotation.x = Math.PI / 2;
      ring.position.y = 0.1 + i * 0.1;
      this.rings.push(ring);
      this.group.add(ring);
    }
  }

  private createGroundGrid() {
    const gridHelper = new THREE.GridHelper(22, 44, 0x3a4cff, 0x0a0a15);
    gridHelper.position.y = 0.01;
    (gridHelper.material as THREE.Material).transparent = true;
    (gridHelper.material as THREE.Material).opacity = 0.15;
    this.group.add(gridHelper);
  }

  private createAmbientParticles() {
    const particleCount = 200;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      // Random position within dome
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI / 2;
      const r = Math.random() * 9;

      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = Math.abs(r * Math.cos(phi));
      positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.05,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending
    });

    const particles = new THREE.Points(geometry, material);
    this.group.add(particles);
  }

  public update() {
    this.time += 0.01;

    // Rotate rings slowly
    this.rings.forEach((ring, i) => {
      ring.rotation.z = this.time * (0.2 + i * 0.1) * (i % 2 === 0 ? 1 : -1);
    });

    // Subtle dome pulse
    const scale = 1 + Math.sin(this.time * 0.5) * 0.02;
    this.dome.scale.set(scale, scale, scale);
  }
}
