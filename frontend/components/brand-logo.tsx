type BrandLogoProps = {
  className?: string;
  compact?: boolean;
};

export function BrandLogo({ className = "", compact = false }: BrandLogoProps) {
  const viewBox = compact ? "0 0 560 150" : "0 0 980 300";

  return (
    <div className={className}>
      <svg
        viewBox={viewBox}
        className="h-auto w-full"
        role="img"
        aria-label="FitFlow logo"
        style={{ filter: "drop-shadow(0 18px 26px rgba(59,130,246,0.25))" }}
      >
        <defs>
          <linearGradient id="fitflow-blue-wave" x1="0%" x2="100%" y1="50%" y2="50%">
            <stop offset="0%" stopColor="#e8f0ff" />
            <stop offset="30%" stopColor="#dfe8ff" />
            <stop offset="65%" stopColor="#b7cdfd" />
            <stop offset="100%" stopColor="#7daaf8" />
          </linearGradient>
        </defs>

        <path
          d="M42 152C90 106 137 89 195 98C254 107 278 141 325 146C386 153 430 119 488 104C561 85 622 89 684 122C739 151 798 154 893 125C895 134 904 156 915 162C915 184 919 198 923 209H41C34 196 40 170 42 152Z"
          fill="url(#fitflow-blue-wave)"
          opacity="0.9"
        />

        <path
          d="M148 96C185 68 242 63 298 83C335 97 370 95 406 81C438 68 468 70 496 81C538 96 580 94 620 84C670 72 729 78 779 100C821 119 855 120 895 105"
          fill="none"
          stroke="url(#fitflow-blue-wave)"
          strokeWidth="20"
          strokeLinecap="round"
          opacity="0.94"
        />

        <text
          x="24"
          y="205"
          fill="#f4f5f7"
          fontSize={compact ? 138 : 180}
          fontWeight={900}
          letterSpacing={compact ? -9 : -12}
          fontFamily="Segoe UI, Arial, sans-serif"
        >
          FitFlow
        </text>
      </svg>
    </div>
  );
}
