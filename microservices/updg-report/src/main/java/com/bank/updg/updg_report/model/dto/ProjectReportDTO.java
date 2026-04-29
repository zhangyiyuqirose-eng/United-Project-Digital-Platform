package com.bank.updg.updg_report.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Project report data transfer object
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProjectReportDTO {

    private String projectName;

    private String projectCode;

    private String status;

    private BigDecimal budget;

    private BigDecimal actualCost;

    private String managerName;

    private LocalDate startDate;

    private LocalDate endDate;

    private BigDecimal cpi;

    private BigDecimal spi;

    private Integer milestoneCount;

    private Integer taskCount;
}
