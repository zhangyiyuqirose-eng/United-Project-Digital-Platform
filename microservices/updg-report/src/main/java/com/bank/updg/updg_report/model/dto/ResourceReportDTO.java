package com.bank.updg.updg_report.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * Resource report data transfer object
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResourceReportDTO {

    private String poolId;

    private String poolName;

    private Integer totalStaff;

    private Integer activeStaff;

    private Integer assignedStaff;

    private String skillDistribution;

    private BigDecimal utilizationRate;
}
