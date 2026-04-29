package com.bank.updg.updg_report.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * Cost report data transfer object
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CostReportDTO {

    private String projectId;

    private String projectName;

    private BigDecimal budgetAmount;

    private BigDecimal totalCost;

    private BigDecimal outsourceCost;

    private BigDecimal laborCost;

    private BigDecimal variance;

    private BigDecimal varianceRate;

    private BigDecimal settlementAmount;
}
