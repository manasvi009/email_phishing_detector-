import { motion } from "framer-motion";

export default function FeatureCard({ icon: Icon, title, description }) {
  return (
    <motion.div
      whileHover={{ y: -6 }}
      transition={{ duration: 0.2 }}
      className="glass-panel group rounded-[30px] p-6"
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-blue-100 bg-blue-50 text-blue-600 transition duration-200 group-hover:border-blue-200">
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="display-title mt-5 text-xl font-bold text-slate-900">{title}</h3>
      <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
    </motion.div>
  );
}
