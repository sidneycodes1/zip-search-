import React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'md', ...props }, ref) => {
    const baseStyles = 'font-medium rounded-lg transition focus:outline-none focus:ring-2 focus:ring-offset-2'
    const variantStyles = {
      default: 'bg-black text-white hover:bg-gray-900 focus:ring-black',
      outline: 'border border-gray-300 text-black hover:bg-gray-50 focus:ring-black',
      ghost: 'text-black hover:bg-gray-100 focus:ring-black',
    }
    const sizeStyles = {
      sm: 'px-3 py-1 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    }

    return (
      <button
        ref={ref}
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
        {...props}
      />
    )
  }
)

Button.displayName = 'Button'
