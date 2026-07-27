import type { ReactNode } from "react";

interface Props {
  title: string;
  value: string | number;
  description?: string;
  icon: ReactNode;
}

export default function StatCard({
  title,
  value,
  description,
  icon,
}: Props) {

  return (
    <div className="
      bg-white
      rounded-xl
      shadow-sm
      p-6
      border
      border-slate-200
      hover:shadow-md
      transition
    ">

      <div className="flex justify-between items-center">

        <div>

          <p className="text-sm text-slate-500">
            {title}
          </p>

          <h2 className="text-3xl font-bold mt-2">
            {value}
          </h2>

          {description && (
            <p className="text-sm text-slate-500 mt-2">
              {description}
            </p>
          )}

        </div>


        <div className="
          p-3
          rounded-lg
        bg-blue-100
          text-blue-600
        ">
          {icon}
        </div>


      </div>

    </div>
  );
}