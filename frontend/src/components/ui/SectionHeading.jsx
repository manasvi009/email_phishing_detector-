import { motion } from "framer-motion";

export default function SectionHeading({ eyebrow, title, description, align = "left" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.45 }}
      className={align === "center" ? "mx-auto max-w-3xl text-center" : "max-w-3xl"}
    >
      {eyebrow ? (
        <span className="eyebrow-chip mb-4">
          {eyebrow}
        </span>
      ) : null}
      <h2 className="display-title text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl md:text-5xl">{title}</h2>
      {description ? <p className="mt-4 text-base leading-7 text-slate-600 sm:text-lg">{description}</p> : null}
    </motion.div>
  );
}
