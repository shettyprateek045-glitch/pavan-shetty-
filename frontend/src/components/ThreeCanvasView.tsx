import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Candidate, Job } from '../types';
import { 
  RotateCcw, 
  Sparkles, 
  Maximize2, 
  Layers, 
  Eye, 
  Info,
  CheckCircle2
} from 'lucide-react';

interface ThreeCanvasViewProps {
  candidates: Candidate[];
  activeJob: Job;
  onSelectCandidate: (candidate: Candidate) => void;
  blindScreening: boolean;
}

export const ThreeCanvasView: React.FC<ThreeCanvasViewProps> = ({
  candidates,
  activeJob,
  onSelectCandidate,
  blindScreening
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredCandidate, setHoveredCandidate] = useState<Candidate | null>(null);
  const [hudPos, setHudPos] = useState({ x: 0, y: 0 });
  const [autoRotate, setAutoRotate] = useState(true);
  const [filterMode, setFilterMode] = useState<'all' | 'shortlisted' | 'review'>('all');

  // Three.js internal references
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const groupRef = useRef<THREE.Group | null>(null);
  const candidateMeshesRef = useRef<{ mesh: THREE.Mesh; candidate: Candidate }[]>([]);
  const mouseRef = useRef({ x: 0, y: 0, targetX: 0, targetY: 0, rawX: 0, rawY: 0 });
  const raycasterRef = useRef(new THREE.Raycaster());

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight || 520;

    // 1. Scene Setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xF8FAFC);
    sceneRef.current = scene;

    // 2. Camera Setup
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 5, 24);
    cameraRef.current = camera;

    // 3. Renderer Setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 4. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x2563EB, 1.2);
    dirLight1.position.set(15, 20, 15);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x0284C7, 0.7);
    dirLight2.position.set(-15, -10, -10);
    scene.add(dirLight2);

    // 5. Main Root Group for Cursor Motion Rotation
    const rootGroup = new THREE.Group();
    scene.add(rootGroup);
    groupRef.current = rootGroup;

    // 6. Central Job Requirement Origin Node (0, 0, 0)
    const targetGeometry = new THREE.SphereGeometry(0.85, 32, 32);
    const targetMaterial = new THREE.MeshStandardMaterial({
      color: 0x0F172A,
      roughness: 0.3,
      metalness: 0.5
    });
    const targetMesh = new THREE.Mesh(targetGeometry, targetMaterial);
    rootGroup.add(targetMesh);

    // Glowing wireframe rings around job origin
    const ringGeo1 = new THREE.RingGeometry(1.4, 1.45, 64);
    const ringMat1 = new THREE.MeshBasicMaterial({ color: 0x2563EB, side: THREE.DoubleSide, transparent: true, opacity: 0.45 });
    const ringMesh1 = new THREE.Mesh(ringGeo1, ringMat1);
    ringMesh1.rotation.x = Math.PI / 2;
    rootGroup.add(ringMesh1);

    const ringGeo2 = new THREE.RingGeometry(2.0, 2.05, 64);
    const ringMat2 = new THREE.MeshBasicMaterial({ color: 0x38BDF8, side: THREE.DoubleSide, transparent: true, opacity: 0.3 });
    const ringMesh2 = new THREE.Mesh(ringGeo2, ringMat2);
    ringMesh2.rotation.y = Math.PI / 3;
    rootGroup.add(ringMesh2);

    // 7. Subtle 3D Spatial Grid Ground Plane
    const gridHelper = new THREE.GridHelper(26, 26, 0xCBD5E1, 0xE2E8F0);
    gridHelper.position.y = -6;
    rootGroup.add(gridHelper);

    // 8. 3D Background Particle Field
    const particleCount = 280;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      particlePositions[i] = (Math.random() - 0.5) * 45;
      particlePositions[i + 1] = (Math.random() - 0.5) * 35;
      particlePositions[i + 2] = (Math.random() - 0.5) * 40;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    const particleMat = new THREE.PointsMaterial({
      size: 0.12,
      color: 0x9CA3AF,
      transparent: true,
      opacity: 0.45
    });
    const particleField = new THREE.Points(particleGeo, particleMat);
    scene.add(particleField);

    // 9. Candidate Spheres & Vector Connectors
    const candidateMeshes: { mesh: THREE.Mesh; candidate: Candidate }[] = [];

    candidates.forEach((cand, idx) => {
      // Map candidate scores to 3D space:
      // X = Keyword Match (centered around 80)
      // Y = Semantic Similarity (centered around 80)
      // Z = Seniority Fit (centered around 6)
      const posX = ((cand.keyword_score - 80) / 20) * 8.5;
      const posY = ((cand.semantic_score - 80) / 20) * 6.5;
      const posZ = ((cand.experience_years - 6) / 4) * 7.5;

      // Color code by match category (Polished Blue & Slate Palette)
      let nodeColor = 0x64748B; // Slate (<75%)
      if (cand.overall_score >= 85) nodeColor = 0x2563EB; // Royal Blue (Exceptional)
      else if (cand.overall_score >= 75) nodeColor = 0x0284C7; // Ocean Blue (Strong)

      const sphereGeo = new THREE.SphereGeometry(0.55, 32, 32);
      const sphereMat = new THREE.MeshStandardMaterial({
        color: nodeColor,
        roughness: 0.25,
        metalness: 0.35
      });
      const sphere = new THREE.Mesh(sphereGeo, sphereMat);
      sphere.position.set(posX, posY, posZ);

      // Vector connection line to origin
      const lineMat = new THREE.LineBasicMaterial({
        color: nodeColor,
        transparent: true,
        opacity: 0.3
      });
      const linePoints = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(posX, posY, posZ)];
      const lineGeo = new THREE.BufferGeometry().setFromPoints(linePoints);
      const vectorLine = new THREE.Line(lineGeo, lineMat);
      rootGroup.add(vectorLine);

      // Subtle pulse halo around candidate node
      const haloGeo = new THREE.RingGeometry(0.75, 0.85, 32);
      const haloMat = new THREE.MeshBasicMaterial({
        color: nodeColor,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.4
      });
      const halo = new THREE.Mesh(haloGeo, haloMat);
      halo.lookAt(camera.position);
      sphere.add(halo);

      rootGroup.add(sphere);
      candidateMeshes.push({ mesh: sphere, candidate: cand });
    });

    candidateMeshesRef.current = candidateMeshes;

    // 10. Animation Loop with Cursor Motion Smoothing
    let animationFrameId: number;
    let baseTime = 0;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      baseTime += 0.01;

      // Gentle auto-rotation or cursor inertia
      if (rootGroup) {
        // Lerp mouse rotation
        mouseRef.current.x += (mouseRef.current.targetX - mouseRef.current.x) * 0.05;
        mouseRef.current.y += (mouseRef.current.targetY - mouseRef.current.y) * 0.05;

        if (autoRotate) {
          rootGroup.rotation.y = mouseRef.current.x + Math.sin(baseTime * 0.4) * 0.2;
        } else {
          rootGroup.rotation.y = mouseRef.current.x;
        }
        rootGroup.rotation.x = mouseRef.current.y;

        // Subtle idle wobble for origin rings
        ringMesh1.rotation.z += 0.005;
        ringMesh2.rotation.z -= 0.004;

        // Animate background star particles
        particleField.rotation.y = mouseRef.current.x * 0.15 + baseTime * 0.02;
      }

      renderer.render(scene, camera);
    };

    animate();

    // Resize Handler
    const handleResize = () => {
      if (!containerRef.current || !renderer || !camera) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight || 520;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      if (renderer.domElement && containerRef.current) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [candidates, autoRotate]);

  // Cursor Motion Listener on Canvas Container
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current || !cameraRef.current || !sceneRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Normalized Device Coordinates (-1 to +1)
    const ndcX = (x / rect.width) * 2 - 1;
    const ndcY = -(y / rect.height) * 2 + 1;

    // Set target rotation based on cursor position
    mouseRef.current.targetX = ndcX * Math.PI * 0.45;
    mouseRef.current.targetY = -ndcY * Math.PI * 0.25;
    mouseRef.current.rawX = x;
    mouseRef.current.rawY = y;

    // Raycast to find hovered candidate
    raycasterRef.current.setFromCamera(new THREE.Vector2(ndcX, ndcY), cameraRef.current);
    const meshes = candidateMeshesRef.current.map(c => c.mesh);
    const intersects = raycasterRef.current.intersectObjects(meshes);

    if (intersects.length > 0) {
      const hitMesh = intersects[0].object as THREE.Mesh;
      const found = candidateMeshesRef.current.find(c => c.mesh === hitMesh);
      if (found) {
        setHoveredCandidate(found.candidate);
        setHudPos({ x, y });
        document.body.style.cursor = 'pointer';
        return;
      }
    }

    setHoveredCandidate(null);
    document.body.style.cursor = 'default';
  };

  const handleCanvasClick = () => {
    if (hoveredCandidate) {
      onSelectCandidate(hoveredCandidate);
    }
  };

  const resetCamera = () => {
    mouseRef.current.targetX = 0;
    mouseRef.current.targetY = 0;
  };

  return (
    <div className="relative w-full h-[580px] bg-card border border-border rounded-xl shadow-subtle overflow-hidden select-none">
      {/* 3D WebGL Canvas Container */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onClick={handleCanvasClick}
        className="w-full h-full cursor-grab active:cursor-grabbing"
      />

      {/* Floating 3D HUD Pill on Node Hover */}
      {hoveredCandidate && (
        <div
          className="absolute pointer-events-none z-30 transition-all duration-75 transform -translate-x-1/2 -translate-y-full mb-3"
          style={{ left: hudPos.x, top: hudPos.y }}
        >
          <div className="bg-primary/95 backdrop-blur-md text-white border border-white/10 rounded-lg p-3 shadow-dropdown w-64 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono uppercase tracking-wider text-accent-light font-bold">
                Rank #{hoveredCandidate.rank || '1'} • 3D Node
              </span>
              <span className="text-xs font-mono font-bold text-success-light">
                {hoveredCandidate.overall_score}% Fit
              </span>
            </div>

            <div>
              <div className="font-semibold text-xs text-white">
                {blindScreening ? `Candidate #${hoveredCandidate.rank}` : hoveredCandidate.name}
              </div>
              <div className="text-[10px] text-gray-300 truncate">
                {hoveredCandidate.title}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-1 py-1 border-y border-white/10 text-[10px] font-mono text-center">
              <div>
                <span className="text-gray-400 block text-[9px]">Semantic</span>
                <span className="text-accent-light font-bold">{hoveredCandidate.semantic_score}%</span>
              </div>
              <div>
                <span className="text-gray-400 block text-[9px]">Keyword</span>
                <span className="text-white font-bold">{hoveredCandidate.keyword_score}%</span>
              </div>
              <div>
                <span className="text-gray-400 block text-[9px]">Exp</span>
                <span className="text-white font-bold">{hoveredCandidate.experience_years}y</span>
              </div>
            </div>

            <div className="text-[10px] text-gray-300 flex items-center justify-between">
              <span>Click node to inspect profile</span>
              <span className="text-accent-light font-semibold">→</span>
            </div>
          </div>
        </div>
      )}

      {/* Top Left Title & 3D Spatial Badge */}
      <div className="absolute top-4 left-4 z-20 pointer-events-none flex items-center gap-2">
        <div className="bg-primary text-white text-[11px] font-semibold px-2.5 py-1 rounded-md shadow-subtle flex items-center gap-1.5 pointer-events-auto">
          <Sparkles className="w-3.5 h-3.5 text-accent" />
          <span>3D Talent Vector Space</span>
        </div>
        <span className="text-[11px] text-secondary bg-white/90 backdrop-blur-sm border border-border px-2.5 py-1 rounded-md shadow-subtle pointer-events-auto font-mono">
          Target: {activeJob.title}
        </span>
      </div>

      {/* Top Right 3D Controls */}
      <div className="absolute top-4 right-4 z-20 flex items-center gap-2">
        <button
          onClick={() => setAutoRotate(!autoRotate)}
          className={`text-xs px-2.5 py-1.5 rounded-md font-medium border shadow-subtle transition-colors flex items-center gap-1.5 ${
            autoRotate
              ? 'bg-accent/10 border-accent/40 text-accent'
              : 'bg-white border-border text-secondary hover:text-primary'
          }`}
        >
          <RotateCcw className={`w-3 h-3 ${autoRotate ? 'animate-spin' : ''}`} />
          <span>Auto-Spin {autoRotate ? 'On' : 'Off'}</span>
        </button>

        <button
          onClick={resetCamera}
          className="text-xs px-2.5 py-1.5 bg-white border border-border text-secondary hover:text-primary rounded-md font-medium shadow-subtle transition-colors"
          title="Reset 3D camera orientation"
        >
          Reset Camera
        </button>
      </div>

      {/* Bottom Left 3D Spatial Axis Guide */}
      <div className="absolute bottom-4 left-4 z-20 bg-white/90 backdrop-blur-sm border border-border rounded-lg p-2.5 shadow-subtle text-[11px] text-secondary space-y-1">
        <div className="font-semibold text-primary text-[10px] uppercase tracking-wider mb-1 flex items-center gap-1">
          <Layers className="w-3 h-3 text-accent" />
          <span>3D Vector Projections</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-primary"></span>
          <span><strong>X-Axis:</strong> Keyword TF-IDF Match</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent"></span>
          <span><strong>Y-Axis:</strong> Semantic Sentence-BERT Height</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-success"></span>
          <span><strong>Z-Axis:</strong> Seniority / Experience Depth</span>
        </div>
      </div>

      {/* Bottom Right Interactive Tip */}
      <div className="absolute bottom-4 right-4 z-20 pointer-events-none text-[11px] text-secondary bg-white/85 backdrop-blur-sm px-3 py-1.5 rounded-md border border-border shadow-subtle">
        Move cursor over canvas to rotate 3D camera • Hover node to inspect
      </div>
    </div>
  );
};
