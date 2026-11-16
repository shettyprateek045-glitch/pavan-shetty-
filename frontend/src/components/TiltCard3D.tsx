import React, { useRef, useState, MouseEvent } from 'react';

interface TiltCard3DProps {
  children: React.ReactNode;
  className?: string;
  maxTilt?: number; // max tilt degrees (e.g. 10)
  onClick?: () => void;
}

export const TiltCard3D: React.FC<TiltCard3DProps> = ({
  children,
  className = '',
  maxTilt = 8,
  onClick
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [cursorPos, setCursorPos] = useState({ x: 50, y: 50 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const width = rect.width;
    const height = rect.height;

    const xPct = (x / width) * 100;
    const yPct = (y / height) * 100;

    // Calculate tilt angles: -maxTilt to +maxTilt
    const tiltX = ((y / height) - 0.5) * -maxTilt * 2;
    const tiltY = ((x / width) - 0.5) * maxTilt * 2;

    setTilt({ x: tiltX, y: tiltY });
    setCursorPos({ x: xPct, y: yPct });
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setTilt({ x: 0, y: 0 });
  };

  return (
    <div
      style={{ perspective: '1000px' }}
      className="inline-block w-full h-full"
    >
      <div
        ref={cardRef}
        onClick={onClick}
        onMouseMove={handleMouseMove}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        style={{
          transform: isHovered
            ? `rotateX(${tilt.x.toFixed(2)}deg) rotateY(${tilt.y.toFixed(2)}deg) scale3d(1.015, 1.015, 1.015)`
            : 'rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)',
          transition: isHovered ? 'transform 0.1s ease-out' : 'transform 0.4s ease-out',
          transformStyle: 'preserve-3d'
        }}
        className={`relative overflow-hidden transition-shadow duration-200 ${
          isHovered ? 'shadow-elevated' : 'shadow-subtle'
        } ${className}`}
      >
        {/* Cursor Specular Light Glare Overlay */}
        {isHovered && (
          <div
            className="pointer-events-none absolute inset-0 z-10 transition-opacity duration-300"
            style={{
              background: `radial-gradient(circle 220px at ${cursorPos.x}% ${cursorPos.y}%, rgba(37, 99, 235, 0.08), transparent 70%)`
            }}
          />
        )}
        <div style={{ transform: 'translateZ(10px)' }}>
          {children}
        </div>
      </div>
    </div>
  );
};
