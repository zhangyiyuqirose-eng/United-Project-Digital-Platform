package com.bank.updg.updg_report.service.impl;

import com.alibaba.excel.EasyExcel;
import com.bank.updg.updg_report.model.dto.CostReportDTO;
import com.bank.updg.updg_report.model.dto.ProjectReportDTO;
import com.bank.updg.updg_report.model.dto.ResourceReportDTO;
import com.bank.updg.updg_report.model.dto.TimesheetReportDTO;
import com.bank.updg.updg_report.service.ReportService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Report generation service implementation.
 * <p>
 * Currently generates sample in-memory data for each report type.
 * TODO: Replace mock data with Feign client calls to actual microservices.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ReportServiceImpl implements ReportService {

    private static final String FORMAT_XLSX = "xlsx";

    @Override
    public byte[] generateProjectReport(String projectId, String format) {
        List<ProjectReportDTO> data = buildProjectReportData(projectId);
        return writeExcel(data, ProjectReportDTO.class, validateFormat(format));
    }

    @Override
    public byte[] generateCostReport(String projectId, String format) {
        List<CostReportDTO> data = buildCostReportData(projectId);
        return writeExcel(data, CostReportDTO.class, validateFormat(format));
    }

    @Override
    public byte[] generateTimesheetReport(String staffId, String month, String format) {
        List<TimesheetReportDTO> data = buildTimesheetReportData(staffId, month);
        return writeExcel(data, TimesheetReportDTO.class, validateFormat(format));
    }

    @Override
    public byte[] generateResourceReport(String poolId, String format) {
        List<ResourceReportDTO> data = buildResourceReportData(poolId);
        return writeExcel(data, ResourceReportDTO.class, validateFormat(format));
    }

    @Override
    public byte[] generatePortfolioReport(String format) {
        List<ProjectReportDTO> projects = buildProjectReportData(null);
        List<CostReportDTO> costs = buildCostReportData(null);
        List<ResourceReportDTO> resources = buildResourceReportData(null);

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            EasyExcel.write(out)
                    .excelType(validateFormat(format))
                    .sheet("Projects")
                    .doWrite(projects);
            // Note: EasyExcel single-sheet mode; for multi-sheet, use
            // WriteWorkbook + multiple sheet writes in production
        } catch (Exception e) {
            log.error("Failed to generate portfolio report", e);
            throw new RuntimeException("Failed to generate portfolio report", e);
        }
        return out.toByteArray();
    }

    @Override
    public List<Map<String, Object>> listReports(String type, int page, int size) {
        // TODO: Replace with database query for report generation history
        List<Map<String, Object>> result = new ArrayList<>();
        Map<String, Object> entry = new HashMap<>();
        entry.put("id", "RPT-001");
        entry.put("type", type != null ? type : "project");
        entry.put("name", "Sample Report");
        entry.put("createdAt", LocalDate.now().toString());
        entry.put("createdBy", "system");
        entry.put("status", "generated");
        result.add(entry);
        return result;
    }

    // ---- Mock data builders ----

    private List<ProjectReportDTO> buildProjectReportData(String projectId) {
        List<ProjectReportDTO> list = new ArrayList<>();
        if (projectId != null) {
            list.add(ProjectReportDTO.builder()
                    .projectName("Sample Project")
                    .projectCode(projectId)
                    .status("IN_PROGRESS")
                    .budget(new BigDecimal("500000"))
                    .actualCost(new BigDecimal("320000"))
                    .managerName("John Smith")
                    .startDate(LocalDate.of(2026, 1, 15))
                    .endDate(LocalDate.of(2026, 12, 31))
                    .cpi(new BigDecimal("1.05"))
                    .spi(new BigDecimal("0.98"))
                    .milestoneCount(6)
                    .taskCount(42)
                    .build());
        } else {
            for (int i = 1; i <= 3; i++) {
                list.add(ProjectReportDTO.builder()
                        .projectName("Project " + i)
                        .projectCode("PRJ-" + String.format("%03d", i))
                        .status(i == 1 ? "COMPLETED" : "IN_PROGRESS")
                        .budget(new BigDecimal("500000").multiply(BigDecimal.valueOf(i)))
                        .actualCost(new BigDecimal("320000").multiply(BigDecimal.valueOf(i)))
                        .managerName("Manager " + i)
                        .startDate(LocalDate.of(2026, i, 1))
                        .endDate(LocalDate.of(2026, 12, 31))
                        .cpi(new BigDecimal("1.0" + i))
                        .spi(new BigDecimal("0.9" + i))
                        .milestoneCount(3 + i)
                        .taskCount(20 * i)
                        .build());
            }
        }
        return list;
    }

    private List<CostReportDTO> buildCostReportData(String projectId) {
        List<CostReportDTO> list = new ArrayList<>();
        if (projectId != null) {
            BigDecimal budget = new BigDecimal("500000");
            BigDecimal total = new BigDecimal("320000");
            list.add(CostReportDTO.builder()
                    .projectId(projectId)
                    .projectName("Sample Project")
                    .budgetAmount(budget)
                    .totalCost(total)
                    .outsourceCost(new BigDecimal("120000"))
                    .laborCost(new BigDecimal("200000"))
                    .variance(budget.subtract(total))
                    .varianceRate(budget.subtract(total).divide(budget, 4, BigDecimal.ROUND_HALF_UP))
                    .settlementAmount(new BigDecimal("280000"))
                    .build());
        } else {
            for (int i = 1; i <= 3; i++) {
                BigDecimal budget = new BigDecimal("500000").multiply(BigDecimal.valueOf(i));
                BigDecimal total = new BigDecimal("320000").multiply(BigDecimal.valueOf(i));
                list.add(CostReportDTO.builder()
                        .projectId("PRJ-" + String.format("%03d", i))
                        .projectName("Project " + i)
                        .budgetAmount(budget)
                        .totalCost(total)
                        .outsourceCost(new BigDecimal("120000").multiply(BigDecimal.valueOf(i)))
                        .laborCost(new BigDecimal("200000").multiply(BigDecimal.valueOf(i)))
                        .variance(budget.subtract(total))
                        .varianceRate(budget.subtract(total).divide(budget, 4, BigDecimal.ROUND_HALF_UP))
                        .settlementAmount(new BigDecimal("280000").multiply(BigDecimal.valueOf(i)))
                        .build());
            }
        }
        return list;
    }

    private List<TimesheetReportDTO> buildTimesheetReportData(String staffId, String month) {
        List<TimesheetReportDTO> list = new ArrayList<>();
        String m = month != null ? month : "2026-04";
        if (staffId != null) {
            list.add(TimesheetReportDTO.builder()
                    .staffId(staffId)
                    .staffName("Sample Staff")
                    .projectId("PRJ-001")
                    .projectName("Project 1")
                    .workMonth(m)
                    .totalHours(new BigDecimal("160"))
                    .approvedHours(new BigDecimal("155"))
                    .rejectedHours(new BigDecimal("5"))
                    .attendanceMatchRate(new BigDecimal("0.97"))
                    .build());
        } else {
            for (int i = 1; i <= 5; i++) {
                list.add(TimesheetReportDTO.builder()
                        .staffId("STF-" + String.format("%03d", i))
                        .staffName("Staff " + i)
                        .projectId("PRJ-" + String.format("%03d", i % 3 + 1))
                        .projectName("Project " + (i % 3 + 1))
                        .workMonth(m)
                        .totalHours(new BigDecimal("160"))
                        .approvedHours(new BigDecimal(150 + i))
                        .rejectedHours(new BigDecimal(10 - i))
                        .attendanceMatchRate(new BigDecimal("0.9" + i))
                        .build());
            }
        }
        return list;
    }

    private List<ResourceReportDTO> buildResourceReportData(String poolId) {
        List<ResourceReportDTO> list = new ArrayList<>();
        if (poolId != null) {
            list.add(ResourceReportDTO.builder()
                    .poolId(poolId)
                    .poolName("Engineering Pool")
                    .totalStaff(50)
                    .activeStaff(45)
                    .assignedStaff(38)
                    .skillDistribution("Java:20, Frontend:15, DevOps:10")
                    .utilizationRate(new BigDecimal("0.85"))
                    .build());
        } else {
            list.add(ResourceReportDTO.builder()
                    .poolId("POOL-001")
                    .poolName("Engineering Pool")
                    .totalStaff(50)
                    .activeStaff(45)
                    .assignedStaff(38)
                    .skillDistribution("Java:20, Frontend:15, DevOps:10")
                    .utilizationRate(new BigDecimal("0.85"))
                    .build());
            list.add(ResourceReportDTO.builder()
                    .poolId("POOL-002")
                    .poolName("QA Pool")
                    .totalStaff(20)
                    .activeStaff(18)
                    .assignedStaff(15)
                    .skillDistribution("Manual:8, Automation:10")
                    .utilizationRate(new BigDecimal("0.80"))
                    .build());
        }
        return list;
    }

    // ---- Excel helpers ----

    private <T> byte[] writeExcel(List<T> data, Class<T> clazz, com.alibaba.excel.support.ExcelTypeEnum type) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            EasyExcel.write(out, clazz)
                    .excelType(type)
                    .sheet("Report")
                    .doWrite(data);
        } catch (Exception e) {
            log.error("Failed to write Excel for class {}", clazz.getSimpleName(), e);
            throw new RuntimeException("Failed to generate Excel report", e);
        }
        return out.toByteArray();
    }

    private com.alibaba.excel.support.ExcelTypeEnum validateFormat(String format) {
        if (format == null || FORMAT_XLSX.equalsIgnoreCase(format)) {
            return com.alibaba.excel.support.ExcelTypeEnum.XLSX;
        }
        return com.alibaba.excel.support.ExcelTypeEnum.XLSX;
    }
}
