package com.bank.updg.updg_report.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * Timesheet report data transfer object
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TimesheetReportDTO {

    private String staffId;

    private String staffName;

    private String projectId;

    private String projectName;

    private String workMonth;

    private BigDecimal totalHours;

    private BigDecimal approvedHours;

    private BigDecimal rejectedHours;

    private BigDecimal attendanceMatchRate;
}
