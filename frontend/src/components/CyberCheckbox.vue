<script setup>
defineProps({
  label: { type: String, default: '' },
  modelValue: { type: Boolean, default: false }
});

const emit = defineEmits(['update:modelValue']);

function handleChange(e) {
  emit('update:modelValue', e.target.checked);
}
</script>

<template>
  <label class="inline-flex items-start gap-3 cursor-pointer group select-none relative">
    <div class="cyber-checkbox-wrapper">
      <div class="cyber-checkbox">
        <input 
          type="checkbox" 
          :checked="modelValue" 
          @change="handleChange" 
        />
        <span class="cyber-checkbox__mark">
          <div class="cyber-checkbox__box">
            <svg class="cyber-checkbox__check" viewBox="0 0 12 10">
              <polyline points="1.5 6 4.5 9 10.5 1"></polyline>
            </svg>
          </div>
          <div class="cyber-checkbox__effects">
            <div class="cyber-checkbox__spark"></div>
            <div class="cyber-checkbox__spark"></div>
            <div class="cyber-checkbox__spark"></div>
            <div class="cyber-checkbox__spark"></div>
          </div>
          <div class="cyber-checkbox__particles">
            <div class="particle-1"></div>
            <div class="particle-2"></div>
            <div class="particle-3"></div>
            <div class="particle-4"></div>
            <div class="particle-5"></div>
            <div class="particle-6"></div>
            <div class="particle-7"></div>
            <div class="particle-8"></div>
          </div>
        </span>
      </div>
    </div>
    
    <span v-if="label" class="text-base font-medium text-brand-dark dark:text-gray-200 transition-colors duration-300 group-hover:text-brand-teal leading-snug pt-[1px]">
      {{ label }}
    </span>
  </label>
</template>

<style scoped>
  /* Wrapper to isolate layout flow from absolute effects */
  .cyber-checkbox-wrapper {
    position: relative;
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    /* Optical fix: push down slightly to align with text cap-height */
    margin-top: 2px; 
  }

  .cyber-checkbox {
    /* Brand Teal for the checkbox color */
    --checkbox-size: 20px;
    --checkbox-color: #00AFB9; 
    --checkbox-check-color: #ffffff;
    --checkbox-hover-color: #008C94;
    --checkbox-spark-offset: -20px;

    position: absolute; /* Take out of flow, rely on wrapper */
    inset: 0;
    cursor: pointer;
    user-select: none;
  }

  .cyber-checkbox input {
    display: none;
  }

  .cyber-checkbox__mark {
    position: relative;
    display: inline-block;
    width: var(--checkbox-size);
    height: var(--checkbox-size);
  }

  .cyber-checkbox__box {
    position: absolute;
    inset: 0;
    border: 2px solid var(--checkbox-color);
    border-radius: 4px;
    background: transparent;
    transition: all 0.2s ease;
  }

  .cyber-checkbox__check {
    position: absolute;
    inset: 0;
    padding: 2px;
    stroke: var(--checkbox-check-color);
    stroke-width: 2px;
    stroke-linecap: round;
    stroke-linejoin: round;
    fill: none;
    transform: scale(0);
    transition: transform 0.2s ease;
  }

  .cyber-checkbox__effects {
    position: absolute;
    inset: var(--checkbox-spark-offset);
    pointer-events: none;
  }

  .cyber-checkbox__spark {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 2px;
    height: 2px;
    background: var(--checkbox-color);
    border-radius: 50%;
    opacity: 0;
    transform-origin: center center;
  }

  /* Hover */
  .cyber-checkbox:hover .cyber-checkbox__box {
    border-color: var(--checkbox-hover-color);
    box-shadow: 0 0 0 2px rgba(0, 175, 185, 0.1);
  }

  /* Checked */
  .cyber-checkbox input:checked + .cyber-checkbox__mark .cyber-checkbox__box {
    background: var(--checkbox-color);
    border-color: var(--checkbox-color);
  }

  .cyber-checkbox input:checked + .cyber-checkbox__mark .cyber-checkbox__check {
    transform: scale(1);
  }

  /* Spark Animation */
  .cyber-checkbox input:checked + .cyber-checkbox__mark .cyber-checkbox__spark {
    animation: spark 0.4s ease-out;
  }

  .cyber-checkbox__spark:nth-child(1) { transform: rotate(0deg) translateX(var(--checkbox-spark-offset)); }
  .cyber-checkbox__spark:nth-child(2) { transform: rotate(90deg) translateX(var(--checkbox-spark-offset)); }
  .cyber-checkbox__spark:nth-child(3) { transform: rotate(180deg) translateX(var(--checkbox-spark-offset)); }
  .cyber-checkbox__spark:nth-child(4) { transform: rotate(270deg) translateX(var(--checkbox-spark-offset)); }

  @keyframes spark {
    0% { opacity: 0; transform: scale(0) rotate(0deg) translateX(var(--checkbox-spark-offset)); }
    50% { opacity: 1; }
    100% { opacity: 0; transform: scale(1) rotate(0deg) translateX(calc(var(--checkbox-spark-offset) * 1.5)); }
  }

  /* Active */
  .cyber-checkbox:active .cyber-checkbox__box {
    transform: scale(0.9);
  }

  .cyber-checkbox__particles {
    position: absolute;
    inset: -50%;
    pointer-events: none;
  }

  .cyber-checkbox__particles div {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: var(--checkbox-color);
    opacity: 0;
  }

  /* Particle animations for check */
  .cyber-checkbox input:checked + .cyber-checkbox__mark .particle-1 { animation: particle-1 0.4s ease-out forwards; }
  .cyber-checkbox input:checked + .cyber-checkbox__mark .particle-2 { animation: particle-2 0.4s ease-out forwards 0.1s; }
  .cyber-checkbox input:checked + .cyber-checkbox__mark .particle-3 { animation: particle-3 0.4s ease-out forwards 0.15s; }
  .cyber-checkbox input:checked + .cyber-checkbox__mark .particle-4 { animation: particle-4 0.4s ease-out forwards 0.05s; }
  .cyber-checkbox input:checked + .cyber-checkbox__mark .particle-5 { animation: particle-5 0.4s ease-out forwards 0.12s; }
  .cyber-checkbox input:checked + .cyber-checkbox__mark .particle-6 { animation: particle-6 0.4s ease-out forwards 0.08s; }
  .cyber-checkbox input:checked + .cyber-checkbox__mark .particle-7 { animation: particle-7 0.4s ease-out forwards 0.18s; }
  .cyber-checkbox input:checked + .cyber-checkbox__mark .particle-8 { animation: particle-8 0.4s ease-out forwards 0.15s; }

  @keyframes particle-1 { 0% { transform: translate(0, 0) scale(0); opacity: 0; } 50% { opacity: 1; } 100% { transform: translate(-20px, -20px) scale(1); opacity: 0; } }
  @keyframes particle-2 { 0% { transform: translate(0, 0) scale(0); opacity: 0; } 50% { opacity: 1; } 100% { transform: translate(20px, -20px) scale(1); opacity: 0; } }
  @keyframes particle-3 { 0% { transform: translate(0, 0) scale(0); opacity: 0; } 50% { opacity: 1; } 100% { transform: translate(20px, 20px) scale(1); opacity: 0; } }
  @keyframes particle-4 { 0% { transform: translate(0, 0) scale(0); opacity: 0; } 50% { opacity: 1; } 100% { transform: translate(-20px, 20px) scale(1); opacity: 0; } }
  @keyframes particle-5 { 0% { transform: translate(0, 0) scale(0); opacity: 0; } 50% { opacity: 1; } 100% { transform: translate(-30px, 0px) scale(1); opacity: 0; } }
  @keyframes particle-6 { 0% { transform: translate(0, 0) scale(0); opacity: 0; } 50% { opacity: 1; } 100% { transform: translate(30px, 0px) scale(1); opacity: 0; } }
  @keyframes particle-7 { 0% { transform: translate(0, 0) scale(0); opacity: 0; } 50% { opacity: 1; } 100% { transform: translate(0px, -30px) scale(1); opacity: 0; } }
  @keyframes particle-8 { 0% { transform: translate(0, 0) scale(0); opacity: 0; } 50% { opacity: 1; } 100% { transform: translate(0px, 30px) scale(1); opacity: 0; } }
</style>
