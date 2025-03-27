package com.catalogap.web.filter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.UUID;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NonNull;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.MDC;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * リクエストIDを設定するFilterです.
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class Slf4jMdcFilter extends OncePerRequestFilter {

  private final String responseHeader;
  private final String mdcTokenKey;
  private final String requestHeader;

  @Override
  protected void doFilterInternal(@NonNull final HttpServletRequest request,
      @NonNull final HttpServletResponse response, @NonNull final FilterChain chain)
      throws java.io.IOException, ServletException {
    try {
      final String token;
      if (!StringUtils.isEmpty(requestHeader)
          && !StringUtils.isEmpty(request.getHeader(requestHeader))) {
        token = request.getHeader(requestHeader);
      } else {
        token = UUID.randomUUID().toString().toUpperCase().replace("-", "");
      }
      MDC.put(mdcTokenKey, token);
      if (!StringUtils.isEmpty(responseHeader)) {
        response.addHeader(responseHeader, token);
      }
      chain.doFilter(request, response);
    } finally {
      MDC.remove(mdcTokenKey);
    }
  }

}
