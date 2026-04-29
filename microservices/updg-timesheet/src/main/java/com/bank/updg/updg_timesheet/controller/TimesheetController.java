package com.bank.updg.updg_timesheet.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.model.ApiResponse;
import com.bank.updg.updg_timesheet.mapper.TimesheetMapper;
import com.bank.updg.updg_timesheet.model.entity.Timesheet;
import com.bank.updg.updg_timesheet.service.TimesheetService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/timesheet")
@RequiredArgsConstructor
public class TimesheetController {

    private final TimesheetService timesheetService;
    private final TimesheetMapper timesheetMapper;

    private void validateTimesheetBody(Map<String, String> body) {
        if (body.get("staffId") == null || body.get("staffId").isBlank()) {
            throw new IllegalArgumentException("staffId不能为空");
        }
        if (body.get("projectId") == null || body.get("projectId").isBlank()) {
            throw new IllegalArgumentException("projectId不能为空");
        }
        if (body.get("workDate") == null || body.get("workDate").isBlank()) {
            throw new IllegalArgumentException("workDate不能为空");
        }
        if (body.get("hours") == null || body.get("hours").isBlank()) {
            throw new IllegalArgumentException("hours不能为空");
        }
    }

    @GetMapping("/list")
    public ApiResponse<Page<Timesheet>> listPage(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(required = false) String projectId,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate dateFrom,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate dateTo) {
        Page<Timesheet> pageObj = new Page<>(page, limit);
        LambdaQueryWrapper<Timesheet> wrapper = new LambdaQueryWrapper<>();
        if (projectId != null) wrapper.eq(Timesheet::getProjectId, projectId);
        if (status != null) wrapper.eq(Timesheet::getCheckStatus, status);
        if (dateFrom != null) wrapper.ge(Timesheet::getWorkDate, dateFrom);
        if (dateTo != null) wrapper.le(Timesheet::getWorkDate, dateTo);
        return ApiResponse.success(timesheetMapper.selectPage(pageObj, wrapper));
    }

    @GetMapping
    public ApiResponse<List<Timesheet>> listAll() {
        return ApiResponse.success(timesheetMapper.selectList(new LambdaQueryWrapper<>()));
    }

    @PostMapping("/create")
    public ApiResponse createTimesheet(@RequestBody Map<String, String> body) {
        validateTimesheetBody(body);
        String staffId = body.get("staffId");
        String projectId = body.get("projectId");
        LocalDate workDate = LocalDate.parse(body.get("workDate"));
        BigDecimal hours = new BigDecimal(body.get("hours"));
        String remark = body.get("remark");
        timesheetService.submit(staffId, projectId, workDate, hours, remark);
        return ApiResponse.success("填报成功");
    }

    @PostMapping
    public ApiResponse submit(@RequestBody Map<String, String> body) {
        validateTimesheetBody(body);
        String staffId = body.get("staffId");
        String projectId = body.get("projectId");
        LocalDate workDate = LocalDate.parse(body.get("workDate"));
        BigDecimal hours = new BigDecimal(body.get("hours"));
        String remark = body.get("remark");
        timesheetService.submit(staffId, projectId, workDate, hours, remark);
        return ApiResponse.success("填报成功");
    }

    @PostMapping("/{timesheetId}/approve")
    public ApiResponse approve(@PathVariable String timesheetId,
                               @RequestBody Map<String, Boolean> body) {
        timesheetService.approve(timesheetId, body.get("approved"));
        return ApiResponse.success("审核成功");
    }

    @GetMapping("/staff/{staffId}")
    public ApiResponse listByStaff(@PathVariable String staffId,
                                   @RequestParam(defaultValue = "1") int page,
                                   @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(timesheetService.listByStaff(staffId, page, size));
    }

    @GetMapping("/project/{projectId}")
    public ApiResponse listByProject(@PathVariable String projectId,
                                     @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
                                     @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to,
                                     @RequestParam(defaultValue = "1") int page,
                                     @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.success(timesheetService.listByProject(projectId, from, to, page, size));
    }

    @GetMapping("/pending")
    public ApiResponse listPending() {
        return ApiResponse.success(timesheetService.listPendingApproval());
    }

    @GetMapping("/staff/{staffId}/total-hours")
    public ApiResponse getTotalHours(@PathVariable String staffId,
                                     @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
                                     @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to) {
        return ApiResponse.success(timesheetService.getTotalHours(staffId, from, to));
    }

    @PostMapping("/batch-approve")
    public ApiResponse batchApprove(@RequestBody Map<String, Object> body) {
        @SuppressWarnings("unchecked")
        List<String> ids = (List<String>) body.get("timesheetIds");
        boolean approved = Boolean.TRUE.equals(body.get("approved"));
        timesheetService.batchApprove(ids, approved);
        return ApiResponse.success("批量审核成功");
    }
}
