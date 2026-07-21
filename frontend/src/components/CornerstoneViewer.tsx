import { useEffect, useRef } from 'react';

interface CornerstoneViewerProps {
  imageUrl?: string;
}

export function CornerstoneViewer({ imageUrl }: CornerstoneViewerProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current || !imageUrl) {
      return;
    }

    const element = containerRef.current;
    element.innerHTML = '<p>Cornerstone viewer placeholder. Connect a DICOM image endpoint to render here.</p>';
  }, [imageUrl]);

  return (
    <div ref={containerRef} style={{ minHeight: 240, border: '1px solid #374151', borderRadius: 8, padding: 12 }} />
  );
}
