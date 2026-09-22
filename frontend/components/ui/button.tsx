import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50";

    const variantStyles = {
      default:
        "bg-primary text-primary-foreground shadow hover:bg-primary/90 bg-indigo-600 text-white hover:bg-indigo-700",
      destructive:
        "bg-red-600 text-white shadow-sm hover:bg-red-700",
      outline:
        "border border-zinc-700/60 bg-transparent shadow-sm hover:bg-zinc-800 text-zinc-200",
      secondary:
        "bg-zinc-800 text-zinc-100 shadow-sm hover:bg-zinc-700",
      ghost: "hover:bg-zinc-800 text-zinc-300 hover:text-white",
      link: "text-indigo-400 underline-offset-4 hover:underline",
    };

    const sizeStyles = {
      default: "h-9 px-4 py-2",
      sm: "h-8 rounded-md px-3 text-xs",
      lg: "h-10 rounded-md px-8 text-base",
      icon: "h-9 w-9",
    };

    return (
      <button
        className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };
