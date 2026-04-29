package com.bank.updg.updg_business.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_business.model.entity.Quotation;

public interface QuotationService extends IService<Quotation> {

    Quotation createQuotation(Quotation data);

    void updateQuotation(String quotationId, Quotation data);

    Quotation getQuotation(String quotationId);

    Page<Quotation> listQuotations(String opportunityId, String status, int page, int size);

    void sendQuotation(String quotationId);

    void acceptQuotation(String quotationId);

    void rejectQuotation(String quotationId);
}
