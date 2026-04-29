package com.bank.updg.updg_project.util;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Map;

/**
 * EVM 挣值管理计算工具
 */
public class EvmCalculator {

    /**
     * 计算成本绩效指数 CPI = EV / AC
     * CPI > 1: 成本节约
     * CPI < 1: 成本超支
     */
    public static BigDecimal calculateCPI(BigDecimal ev, BigDecimal ac) {
        if (ac.compareTo(BigDecimal.ZERO) == 0) return BigDecimal.ZERO;
        return ev.divide(ac, 4, RoundingMode.HALF_UP);
    }

    /**
     * 计算进度绩效指数 SPI = EV / PV
     * SPI > 1: 进度提前
     * SPI < 1: 进度落后
     */
    public static BigDecimal calculateSPI(BigDecimal ev, BigDecimal pv) {
        if (pv.compareTo(BigDecimal.ZERO) == 0) return BigDecimal.ZERO;
        return ev.divide(pv, 4, RoundingMode.HALF_UP);
    }

    /**
     * 计算成本偏差 CV = EV - AC
     */
    public static BigDecimal calculateCV(BigDecimal ev, BigDecimal ac) {
        return ev.subtract(ac);
    }

    /**
     * 计算进度偏差 SV = EV - PV
     */
    public static BigDecimal calculateSV(BigDecimal ev, BigDecimal pv) {
        return ev.subtract(pv);
    }

    /**
     * 计算完工估算 EAC = BAC / CPI
     */
    public static BigDecimal calculateEAC(BigDecimal bac, BigDecimal cpi) {
        if (cpi.compareTo(BigDecimal.ZERO) == 0) return bac;
        return bac.divide(cpi, 2, RoundingMode.HALF_UP);
    }

    /**
     * 构建 EVM 指标结果
     */
    public static Map<String, Object> buildResult(BigDecimal pv, BigDecimal ev, BigDecimal ac) {
        BigDecimal cpi = calculateCPI(ev, ac);
        BigDecimal spi = calculateSPI(ev, pv);
        BigDecimal cv = calculateCV(ev, ac);
        BigDecimal sv = calculateSV(ev, pv);

        return Map.of(
                "pv", pv, "ev", ev, "ac", ac,
                "cpi", cpi, "spi", spi,
                "cv", cv, "sv", sv,
                "costWarning", cpi.compareTo(new BigDecimal("0.9")) < 0,
                "scheduleWarning", spi.compareTo(new BigDecimal("0.9")) < 0
        );
    }
}
