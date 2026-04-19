export function QuantumBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div
        className="absolute inset-0 opacity-[0.5]"
        style={{
          backgroundImage:
            "radial-gradient(circle at 50% 0%, oklch(0.95 0 0), transparent 60%)",
        }}
      />
    </div>
  );
}
